import numpy as np

class Quaternion:
    """
    Quaternion class for INS rotation management.
    Uses scalar-first [w, x, y, z] convention internally.
    """
    def __init__(self, q: np.ndarray = np.array([1.0, 0.0, 0.0, 0.0])):
        self.q = np.array(q, dtype=float)
        self.normalize()
        
    def normalize(self):
        norm = np.linalg.norm(self.q)
        if norm > 1e-10:
            self.q /= norm
            
    def to_matrix(self) -> np.ndarray:
        w, x, y, z = self.q
        return np.array([
            [1 - 2*(y*y + z*z), 2*(x*y - w*z), 2*(x*z + w*y)],
            [2*(x*y + w*z), 1 - 2*(x*x + z*z), 2*(y*z - w*x)],
            [2*(x*z - w*y), 2*(y*z + w*x), 1 - 2*(x*x + y*y)]
        ])
        
    def update(self, angular_rate: np.ndarray, dt: float):
        """
        Updates the quaternion given an angular rate vector (rad/s) and time step dt.
        """
        w = angular_rate * dt
        theta = np.linalg.norm(w)
        
        if theta > 1e-8:
            s_half_theta = np.sin(theta / 2.0)
            c_half_theta = np.cos(theta / 2.0)
            dq = np.array([
                c_half_theta,
                w[0] / theta * s_half_theta,
                w[1] / theta * s_half_theta,
                w[2] / theta * s_half_theta
            ])
        else:
            dq = np.array([1.0, 0.5 * w[0], 0.5 * w[1], 0.5 * w[2]])
            
        self.q = self._multiply(self.q, dq)
        self.normalize()
        
    @staticmethod
    def _multiply(q1: np.ndarray, q2: np.ndarray) -> np.ndarray:
        w1, x1, y1, z1 = q1
        w2, x2, y2, z2 = q2
        return np.array([
            w1*w2 - x1*x2 - y1*y2 - z1*z2,
            w1*x2 + x1*w2 + y1*z2 - z1*y2,
            w1*y2 - x1*z2 + y1*w2 + z1*x2,
            w1*z2 + x1*y2 - y1*x2 + z1*w2
        ])
