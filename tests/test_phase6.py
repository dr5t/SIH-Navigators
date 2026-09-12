import unittest
import numpy as np
from navigation_core.map_matching.matcher import snap_to_road

class TestPhase6(unittest.TestCase):
    def test_snap_to_road(self):
        # One segment from (0,0) to (10,0)
        segments = np.array([
            [[0.0, 0.0], [10.0, 0.0]],
            [[10.0, 0.0], [10.0, 10.0]]
        ])
        
        # Test point above the first segment
        p1 = np.array([5.0, 2.0])
        snapped1 = snap_to_road(p1, segments)
        np.testing.assert_almost_equal(snapped1, [5.0, 0.0])
        
        # Test point past the end of the first segment (should clamp or jump to second)
        # Point is at (12, 1). Closest to the second vertical segment [10, 0] to [10, 10]
        p2 = np.array([12.0, 2.0])
        snapped2 = snap_to_road(p2, segments)
        np.testing.assert_almost_equal(snapped2, [10.0, 2.0])
        
        # Test empty segments
        snapped3 = snap_to_road(np.array([1.0, 1.0]), np.array([]))
        np.testing.assert_almost_equal(snapped3, [1.0, 1.0])

if __name__ == '__main__':
    unittest.main()
