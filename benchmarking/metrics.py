import numpy as np
from typing import Dict

def calculate_rmse(estimated: np.ndarray, ground_truth: np.ndarray) -> float:
    """
    Calculate the Root Mean Square Error (RMSE) between estimated and ground truth arrays.
    Assumes arrays are of the same shape (N, D).
    """
    if len(estimated) == 0 or len(ground_truth) == 0:
        return 0.0
    
    diff = estimated - ground_truth
    mse = np.mean(np.sum(diff**2, axis=1))
    return np.sqrt(mse)

def evaluate_trajectory(estimated_traj: list, ground_truth_traj: list) -> Dict[str, float]:
    """
    Evaluates an estimated trajectory against a ground truth trajectory.
    Both inputs are expected to be lists of dictionaries with 'pos' (3D vector) and 'vel' (3D vector).
    Assumes trajectories are time-aligned.
    """
    n_points = min(len(estimated_traj), len(ground_truth_traj))
    
    if n_points == 0:
        return {"pos_rmse": 0.0, "vel_rmse": 0.0, "2d_pos_rmse": 0.0}
        
    est_pos = np.array([pt['pos'] for pt in estimated_traj[:n_points]])
    gt_pos = np.array([pt['pos'] for pt in ground_truth_traj[:n_points]])
    
    est_vel = np.array([pt['vel'] for pt in estimated_traj[:n_points]])
    gt_vel = np.array([pt['vel'] for pt in ground_truth_traj[:n_points]])
    
    return {
        "pos_rmse": calculate_rmse(est_pos, gt_pos),
        "2d_pos_rmse": calculate_rmse(est_pos[:, 0:2], gt_pos[:, 0:2]),
        "vel_rmse": calculate_rmse(est_vel, gt_vel)
    }
