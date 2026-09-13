import numpy as np
from typing import Dict, Any

from navigation_core.sensors.types import IMUMeasurement, GNSSMeasurement, SensorType, SensorSource, GNSSQuality
from navigation_core.sensors.sync import SensorSynchronizer
from navigation_core.filtering.attitude import AttitudeEstimator
from navigation_core.alignment.alignment import FrameAlignment
from navigation_core.fusion.state_machine import NavigationStateMachine, NavigationMode
from navigation_core.fusion.eskf import ErrorStateEKF
from navigation_core.ai.speed_estimator import AISpeedEstimator
from navigation_core.constraints.vehicle import NonHolonomicConstraints
from navigation_core.map_matching.offline_map import LocalMapPackage
from navigation_core.map_matching.matcher import MapMatcher
from navigation_core.state import NavigationState

class NavigationEngine:
    """
    The top-level orchestrator for the Navigators Core Navigation Engine.
    This class is instantiated by Chaquopy in Android (PythonBridge.kt).
    """
    def __init__(self, ref_lat: float, ref_lon: float, ref_alt: float):
        self.ref_lat = ref_lat
        self.ref_lon = ref_lon
        self.ref_alt = ref_alt
        
        # Phases 1 & 2: Sync and Health
        self.sync = SensorSynchronizer(max_delay_ms=50.0)
        
        # Phases 3 & 4: Alignment and Attitude
        self.alignment = FrameAlignment()
        self.attitude = AttitudeEstimator(beta=0.1)
        
        # Phases 5: AI Speed
        self.speed_estimator = AISpeedEstimator()
        
        # Phase 7: Constraints
        self.nhc = NonHolonomicConstraints()
        
        # Phases 8 & 9: State Machine
        self.state_machine = NavigationStateMachine()
        
        # Phase 10: ESKF
        self.eskf = ErrorStateEKF()
        
        # Map Matching
        self.map_provider = LocalMapPackage("map_package.json")
        self.map_provider.load_region("default") # Attempts to load if exists
        self.map_matcher = MapMatcher(self.map_provider)
        
        # History for AI Model (sliding window)
        self.accel_window = []
        
        self.current_time = 0.0
        self.last_state = self._build_state()

    def process_imu(self, accel: np.ndarray, gyro: np.ndarray, dt: float, timestamp: float, is_external: bool = False) -> Dict[str, Any]:
        """
        Processes a single IMU tick. Called directly from Android SensorEventListener or ExternalImuService.
        """
        self.current_time = timestamp
        
        # Sync & Health (Phase 2)
        source = SensorSource.LIVE_ANDROID if not is_external else SensorSource.EXTERNAL
        meas = IMUMeasurement(timestamp, SensorType.ACCELEROMETER, accel[0], accel[1], accel[2], 1.0, source, 0)
        health = self.sync.check_health(meas)
        
        # Attitude (Phase 4)
        self.attitude.update(gyro, accel, dt)
        
        # ESKF Predict
        self.eskf.predict(accel, gyro, dt)
        
        # State Machine (Check for GNSS timeout)
        self.state_machine.process_imu(timestamp)
        
        # Non-Holonomic Constraints update if in DR
        if self.state_machine.mode in [NavigationMode.DEAD_RECKONING, NavigationMode.DEAD_RECKONING_DEGRADED]:
            v_nav = self.eskf.ins.vel
            q = self.eskf.ins.q
            innovation, H, R = self.nhc.generate_virtual_measurements(v_nav, q)
            self.eskf.update_virtual(innovation, H, R)
            
        self.last_state = self._build_state()
        
        # Map Matching Observation
        match = self.map_matcher.update(self.last_state)
        if match and match.confidence > 0.3:
            self.last_state.map_matched_lat = match.projected_lat
            self.last_state.map_matched_lon = match.projected_lon
            self.last_state.matched_road_id = match.segment.road_id
            self.last_state.map_match_confidence = match.confidence
            
            # Constrain position in ESKF if high confidence
            if match.confidence > 0.8:
                # Convert matched lat/lon to ENU
                from navigation_core.ins.coordinates import lla_to_enu
                pos_enu = lla_to_enu(match.projected_lat, match.projected_lon, self.last_state.altitude, 
                                     self.ref_lat, self.ref_lon, self.ref_alt)
                
                # Apply as virtual measurement with uncertainty inversely proportional to confidence
                R_map = np.eye(3) * (5.0 / max(0.1, match.confidence))**2
                innovation = pos_enu - self.eskf.ins.pos
                H_map = np.zeros((3, 15))
                H_map[0:3, 0:3] = np.eye(3)
                self.eskf.update_virtual(innovation, H_map, R_map)
                
                # Re-build state after constraint
                self.last_state = self._build_state()
                self.last_state.map_matched_lat = match.projected_lat
                self.last_state.map_matched_lon = match.projected_lon
                self.last_state.matched_road_id = match.segment.road_id
                self.last_state.map_match_confidence = match.confidence
        return self._state_to_dict()

    def process_gnss(self, lat: float, lon: float, alt: float, speed: float, course: float, h_acc: float, timestamp: float) -> Dict[str, Any]:
        """
        Processes a single GNSS tick.
        """
        # Latency/Staleness Check
        # If the GNSS timestamp is significantly older than our current time, it's stale
        if self.current_time > 0 and (self.current_time - timestamp) > 1.5:
            # Stale GNSS, ignore completely to prevent backward time jumps
            return self._state_to_dict()
            
        self.current_time = timestamp
        
        quality = GNSSQuality.GOOD if h_acc < 10.0 else GNSSQuality.DEGRADED
        meas = GNSSMeasurement(timestamp, lat, lon, alt, speed, course, h_acc, h_acc, "gps", quality, 8, SensorSource.LIVE_ANDROID, 0)
        
        # Sync & Health
        health = self.sync.sync_gnss(meas)
        
        # Speed inconsistency check
        ins_speed = np.linalg.norm(self.eskf.ins.vel)
        if abs(speed - ins_speed) > 15.0: # m/s (approx 54 km/h jump)
            # Gross speed inconsistency, likely an outlier
            quality = GNSSQuality.DEGRADED
            meas.quality = quality
            h_acc = max(h_acc, 20.0) # Inflate reported accuracy

        # State Machine process initially
        mode_before = self.state_machine.mode
        new_mode = self.state_machine.process_gnss(meas, timestamp, self.last_state)
        
        if mode_before == NavigationMode.INITIALIZING:
            # Seed the ESKF with the first GNSS fix
            from navigation_core.ins.coordinates import lla_to_enu
            pos_enu = lla_to_enu(lat, lon, alt, self.ref_lat, self.ref_lon, self.ref_alt)
            course_rad = np.radians(course)
            self.eskf.ins.pos = pos_enu
            self.eskf.ins.vel = np.array([speed * np.sin(course_rad), speed * np.cos(course_rad), 0.0])
            
        elif new_mode in [NavigationMode.GNSS_GOOD, NavigationMode.GNSS_DEGRADED]:
            # Convert speed/course to VN, VE
            course_rad = np.radians(course)
            vn = speed * np.cos(course_rad)
            ve = speed * np.sin(course_rad)
            vd = 0.0 # Assuming mostly flat for basic GNSS
            
            from navigation_core.ins.coordinates import lla_to_enu
            pos_enu = lla_to_enu(lat, lon, alt, self.ref_lat, self.ref_lon, self.ref_alt)
            vel_enu = np.array([ve, vn, -vd])
            
            R_meas = np.zeros((6, 6))
            R_meas[0:3, 0:3] = np.eye(3) * (h_acc ** 2)
            R_meas[3:6, 3:6] = np.eye(3) * ((h_acc/2.0) ** 2)
            
            accepted = self.eskf.update_gnss(pos_enu, vel_enu, R_meas)
            if not accepted:
                # The ESKF rejected the measurement (massive outlier)
                # Re-evaluate state machine with rejection flag
                self.state_machine.process_gnss(meas, timestamp, self.last_state, rejected_by_filter=True)
            
        self.last_state = self._build_state()
        return self._state_to_dict()

    def _build_state(self) -> NavigationState:
        r, p, y = self.attitude.get_euler_angles()
        return NavigationState(
            timestamp=self.current_time,
            latitude=self.ref_lat + (self.eskf.ins.pos[1] / 111000.0), # Approximate LLA from ENU
            longitude=self.ref_lon + (self.eskf.ins.pos[0] / (111000.0 * np.cos(np.radians(self.ref_lat)))),
            altitude=self.ref_alt + self.eskf.ins.pos[2],
            velocity_east=self.eskf.ins.vel[0],
            velocity_north=self.eskf.ins.vel[1],
            velocity_up=self.eskf.ins.vel[2],
            roll=r,
            pitch=p,
            yaw=y,
            mode=self.state_machine.mode,
            pos_uncertainty=np.sqrt(self.eskf.P[0,0] + self.eskf.P[1,1]),
            vel_uncertainty=np.sqrt(self.eskf.P[3,3] + self.eskf.P[4,4])
        )

    def _state_to_dict(self) -> Dict[str, Any]:
        s = self.last_state
        return {
            "timestamp": s.timestamp,
            "lat": s.latitude,
            "lon": s.longitude,
            "alt": s.altitude,
            "speed": s.speed_m_s,
            "course": np.degrees(np.arctan2(s.velocity_east, s.velocity_north)),
            "mode": s.mode.name,
            "pos_uncertainty": s.pos_uncertainty,
            "explanation": s.get_confidence_explanation(),
            "map_status": s.map_status,
            "map_matched_lat": s.map_matched_lat,
            "map_matched_lon": s.map_matched_lon,
            "matched_road_id": s.matched_road_id,
            "map_match_confidence": s.map_match_confidence
        }
