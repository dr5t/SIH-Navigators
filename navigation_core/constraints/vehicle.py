import numpy as np
from typing import Tuple
from navigation_core.ins.quaternion import Quaternion

class NonHolonomicConstraints:
    def __init__(self, apply_lateral: bool = True, apply_vertical: bool = True, noise_std: float = 0.1):
        self.apply_lateral = apply_lateral
        self.apply_vertical = apply_vertical
        self.noise_std = noise_std
        
    def generate_virtual_measurements(self, v_nav: np.ndarray, q_vehicle_to_nav: Quaternion) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Calculates the expected lateral and vertical velocity in the vehicle frame
        (which should be zero) and compares it with the current navigation frame velocity
        transformed into the vehicle frame.
        
        Args:
            v_nav: Velocity in navigation frame (ENU)
            q_vehicle_to_nav: Quaternion from vehicle frame to nav frame
            
        Returns:
            v_meas: Virtual velocity measurement in vehicle frame (y, z components should be 0)
            H: Measurement Jacobian relating vehicle frame velocity to nav frame velocity
            R: Measurement covariance
        """
        # Transform nav velocity to vehicle frame
        # v_veh = R_nav2veh * v_nav
        # where R_nav2veh is the transpose/inverse of R_veh2nav
        R_v2n = q_vehicle_to_nav.to_matrix()
        R_n2v = R_v2n.T
        
        v_veh = R_n2v @ v_nav
        
        # We only apply constraints on y (lateral) and z (vertical)
        # So our measurement is just [v_y, v_z] = [0, 0]
        # And the prediction is [v_veh[1], v_veh[2]]
        
        v_meas = np.zeros(2)
        v_pred = np.array([v_veh[1], v_veh[2]])
        
        # Innovation (measurement - prediction)
        innovation = v_meas - v_pred
        
        # Jacobian H mapping from delta_x to delta_v_veh (y, z)
        # delta_v_veh = R_n2v * delta_v_nav
        # We only care about rows 1 and 2, mapped to the velocity error state (indices 3:6)
        H = np.zeros((2, 15))
        H[:, 3:6] = R_n2v[1:3, :]
        
        R = np.eye(2) * (self.noise_std ** 2)
        
        return innovation, H, R
