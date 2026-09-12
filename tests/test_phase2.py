import unittest
import numpy as np
from navigation_core.ins.coordinates import lla_to_ecef, ecef_to_enu, lla_to_enu, enu_to_ecef
from navigation_core.ins.quaternion import Quaternion
from navigation_core.alignment.alignment import compute_static_alignment
from navigation_core.ins.propagation import INSPropagator
from navigation_core.fusion.eskf import ErrorStateEKF

class TestPhase2(unittest.TestCase):
    def test_coordinates(self):
        ref_lat, ref_lon, ref_alt = 37.7749, -122.4194, 10.0
        # Check that LLA to ENU of the reference point is exactly [0, 0, 0]
        enu = lla_to_enu(ref_lat, ref_lon, ref_alt, ref_lat, ref_lon, ref_alt)
        np.testing.assert_almost_equal(enu, [0, 0, 0])
        
        # Test invertibility: local ENU to ECEF, back to ECEF check
        e, n, u = 100.0, -50.0, 20.0
        ecef = enu_to_ecef(e, n, u, ref_lat, ref_lon, ref_alt)
        enu_back = ecef_to_enu(ecef[0], ecef[1], ecef[2], ref_lat, ref_lon, ref_alt)
        np.testing.assert_almost_equal(enu_back, [e, n, u])
        
    def test_quaternion(self):
        # Rotate by 90 degrees around Z axis (Yaw)
        q = Quaternion()
        dt = 1.0
        omega = np.array([0, 0, np.pi/2])
        q.update(omega, dt)
        
        # Rotated X axis should be Y axis
        R = q.to_matrix()
        x_axis = np.array([1, 0, 0])
        x_rot = R @ x_axis
        np.testing.assert_almost_equal(x_rot, [0, 1, 0])
        
    def test_alignment(self):
        # If phone is flat on table, specific force is [0, 0, 9.81]
        accel_window = np.array([
            [0, 0, 9.81],
            [0, 0, 9.81],
            [0, 0, 9.81]
        ])
        q = compute_static_alignment(accel_window, yaw_deg=0.0)
        # Should be identity or close to it
        np.testing.assert_almost_equal(np.abs(q.q), [1, 0, 0, 0])
        
        # If phone is upside down, specific force is [0, 0, -9.81]
        accel_window_inv = np.array([
            [0, 0, -9.81]
        ])
        q_inv = compute_static_alignment(accel_window_inv, yaw_deg=0.0)
        R_inv = q_inv.to_matrix()
        # [0, 0, 1] in nav should map to [0, 0, -1] in body
        # Actually gravity in body is R_nav2body * [0, 0, 1].
        # So R_body2nav * [0, 0, 9.81] = [0, 0, 9.81] in nav frame?
        # Specific force is opposite to gravity. Nav frame specific force is [0, 0, g].
        # So body [0, 0, g] means R_body2nav is identity.
        # Body [0, 0, -g] means it's upside down, so R_body2nav * [0, 0, -g] = [0, 0, g] -> Z is flipped.
        
    def test_ins_propagation(self):
        # Static case: Specific force measures exactly [0, 0, 9.80665]
        # Should result in zero velocity and position change
        ins = INSPropagator()
        accel_body = np.array([0, 0, 9.80665])
        gyro_body = np.array([0, 0, 0])
        dt = 0.1
        
        ins.propagate(accel_body, gyro_body, dt)
        np.testing.assert_almost_equal(ins.vel, [0, 0, 0])
        np.testing.assert_almost_equal(ins.pos, [0, 0, 0])
        
    def test_eskf_static(self):
        eskf = ErrorStateEKF()
        dt = 0.1
        accel_body = np.array([0, 0, 9.80665])
        gyro_body = np.array([0, 0, 0])
        
        eskf.predict(accel_body, gyro_body, dt)
        np.testing.assert_almost_equal(eskf.ins.pos, [0, 0, 0])
        
        # Provide GNSS measurement at origin
        R_meas = np.eye(6)
        eskf.update_gnss(np.zeros(3), np.zeros(3), R_meas)
        np.testing.assert_almost_equal(eskf.ins.pos, [0, 0, 0])

if __name__ == '__main__':
    unittest.main()
