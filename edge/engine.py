import numpy as np
from typing import List, Dict, Optional
from navigation_core.fusion.gnss_fusion import GNSSFusionEngine
from navigation_core.constraints.constraints import is_stationary, apply_zupt, apply_nhc
from navigation_core.map_matching.matcher import snap_to_road

class EdgeEngine:
    """
    Orchestrates the entire navigation pipeline: ESKF, constraints, map matching, and ML.
    Designed to run efficiently on an Android edge device via Chaquopy.
    """
    def __init__(self, ref_lat: float, ref_lon: float, ref_alt: float, road_segments: np.ndarray = np.array([])):
        self.fusion = GNSSFusionEngine(ref_lat, ref_lon, ref_alt)
        self.road_segments = road_segments
        
        self.accel_buffer = []
        self.gyro_buffer = []
        self.buffer_size = 50  # For ZUPT detection
        
        self.trajectory = []
        
    def process_imu(self, accel: np.ndarray, gyro: np.ndarray, dt: float, timestamp: float):
        """Step 1: Process IMU and apply constraints."""
        # 1. Update nominal ESKF state
        self.fusion.process_imu(accel, gyro, dt)
        
        # 2. Maintain buffers for motion state classification
        self.accel_buffer.append(accel)
        self.gyro_buffer.append(gyro)
        if len(self.accel_buffer) > self.buffer_size:
            self.accel_buffer.pop(0)
            self.gyro_buffer.pop(0)
            
        # 3. Apply constraints if buffer is full
        if len(self.accel_buffer) == self.buffer_size:
            acc_win = np.array(self.accel_buffer)
            gyr_win = np.array(self.gyro_buffer)
            
            if is_stationary(acc_win, gyr_win):
                apply_zupt(self.fusion.eskf)
            else:
                apply_nhc(self.fusion.eskf)
                
        # 4. Optional Map Matching
        pos = self.fusion.eskf.ins.pos
        if len(self.road_segments) > 0:
            pos_2d = pos[0:2]
            snapped = snap_to_road(pos_2d, self.road_segments)
            pos[0:2] = snapped
            
        # 5. Log state
        self.trajectory.append({
            'timestamp': timestamp,
            'pos': pos.copy(),
            'vel': self.fusion.eskf.ins.vel.copy()
        })
        
    def process_gnss(self, lat: float, lon: float, alt: float, vn: float, ve: float, vd: float, pos_std: float, vel_std: float):
        """Step 2: Process GNSS updates when available."""
        self.fusion.process_gnss(lat, lon, alt, vn, ve, vd, pos_std, vel_std)
