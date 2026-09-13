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
from navigation_core.state import NavigationState

class NavigationEngine:
    """
    The top-level orchestrator for the Navigators Core Navigation Engine.
    This class is instantiated by Chaquopy in Android (PythonBridge.kt).
    """
    def __init__(self, ref_lat: float, ref_lon: float, ref_alt: float, ai_model_version: str = "v1.4"):
        self.ref_lat = ref_lat
        self.ref_lon = ref_lon
        self.ref_alt = ref_alt
        
        # Phases 1 & 2: Sync and Health
        self.sync = SensorSynchronizer(max_delay_ms=50.0)
        
        # Phases 3 & 4: Alignment and Attitude
        self.alignment = FrameAlignment()
        self.attitude = AttitudeEstimator(beta=0.1)
        
        # Phases 5: AI Speed
        self.speed_estimator = AISpeedEstimator(version=ai_model_version)
        
        # Phase 7: Constraints
        self.nhc = NonHolonomicConstraints()
        
        # Phases 8 & 9: State Machine
        self.state_machine = NavigationStateMachine()
        
        # Phase 10: ESKF
        self.eskf = ErrorStateEKF()
        
        # History for AI Model (sliding window)
        self.accel_window = []
        
        self.current_time = 0.0
        self.last_state = self._build_state()
        self.active_profile = None
        
        # Configuration Toggles for Navigation Lab Replay
        self.enable_nhc = True
        self.enable_ai = True
        self.enable_map_match = True

    def configure_features(self, nhc: bool = True, ai: bool = True, map_match: bool = True):
        self.enable_nhc = nhc
        self.enable_ai = ai
        self.enable_map_match = map_match

    def load_calibration(self, is_calibrated: bool, alignment_params: Dict[str, Any] = None):
        """
        Loads the calibration and alignment configuration from the active profile.
        """
        self.alignment.is_calibrated = is_calibrated
        self.active_profile = {
            "is_calibrated": is_calibrated,
            "alignment_params": alignment_params
        }
        if alignment_params and 'q_vehicle_to_nav' in alignment_params:
            q = alignment_params['q_vehicle_to_nav']
            from navigation_core.ins.quaternion import Quaternion
            self.alignment.q_vehicle_to_nav = Quaternion(q)

    def process_imu(self, accel: np.ndarray, gyro: np.ndarray, dt: float, timestamp: float) -> Dict[str, Any]:
        """
        Processes a single IMU tick. Called directly from Android SensorEventListener.
        """
        accel = np.asarray(accel, dtype=float)
        gyro = np.asarray(gyro, dtype=float)
        self.current_time = timestamp
        
        # Sync & Health (Phase 2)
        meas = IMUMeasurement(timestamp, SensorType.ACCELEROMETER, accel[0], accel[1], accel[2], 1.0, SensorSource.LIVE_ANDROID, 0)
        health = self.sync.check_health(meas)
        
        # Attitude (Phase 4)
        self.attitude.update(gyro, accel, dt)
        
        # ESKF Predict
        self.eskf.predict(accel, gyro, dt)
        
        # State Machine (Check for GNSS timeout)
        self.state_machine.process_imu(timestamp)
        
        # Non-Holonomic Constraints update if in DR
        if self.enable_nhc and self.state_machine.mode in [NavigationMode.DEAD_RECKONING, NavigationMode.DEAD_RECKONING_DEGRADED]:
            v_nav = self.eskf.ins.vel
            q = self.eskf.ins.q
            innovation, H, R = self.nhc.generate_virtual_measurements(v_nav, q)
            self.eskf.update_virtual(innovation, H, R)
            
        self.last_state = self._build_state()
        return self._state_to_dict()

    def process_gnss(self, lat: float, lon: float, alt: float, speed: float, course: float, h_acc: float, timestamp: float) -> Dict[str, Any]:
        """
        Processes a single GNSS tick.
        """
        self.current_time = timestamp
        
        quality = GNSSQuality.GOOD if h_acc < 10.0 else GNSSQuality.DEGRADED
        meas = GNSSMeasurement(timestamp, lat, lon, alt, speed, course, h_acc, h_acc, "gps", quality, 8, SensorSource.LIVE_ANDROID, 0)
        
        # Sync & Health
        health = self.sync.sync_gnss(meas)
        
        # State Machine
        self.state_machine.process_gnss(meas, timestamp)
        
        if self.state_machine.mode in [NavigationMode.GNSS_GOOD, NavigationMode.GNSS_DEGRADED]:
            # Convert speed/course to VN, VE
            course_rad = np.radians(course)
            vn = speed * np.cos(course_rad)
            ve = speed * np.sin(course_rad)
            vd = 0.0 # Assuming mostly flat for basic GNSS
            
            # Use gnss_fusion logic from Phase 10
            # For brevity, using raw ENU conversion here
            from navigation_core.ins.coordinates import lla_to_enu
            pos_enu = lla_to_enu(lat, lon, alt, self.ref_lat, self.ref_lon, self.ref_alt)
            vel_enu = np.array([ve, vn, -vd])
            
            R_meas = np.zeros((6, 6))
            R_meas[0:3, 0:3] = np.eye(3) * (h_acc ** 2)
            R_meas[3:6, 3:6] = np.eye(3) * ((h_acc/2.0) ** 2)
            
            self.eskf.update_gnss(pos_enu, vel_enu, R_meas)
            
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
            "confidence": s.get_confidence_explanation()["confidence"],
            "ai_status": "ACTIVE" if self.speed_estimator.is_available and self.speed_estimator.last_inference_latency_ms > 0 else "UNAVAILABLE",
            "heading_valid": s.speed_m_s > 0.5
        }
