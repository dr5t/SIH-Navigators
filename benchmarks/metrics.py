import math
import numpy as np
from typing import List, Dict, Any, Tuple
from navigation_core.map_matching.offline_map import RoadSegment

def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates the great-circle distance between two points in meters."""
    return RoadSegment._haversine(lat1, lon1, lat2, lon2)

def calculate_position_errors(est_lats: np.ndarray, est_lons: np.ndarray, gt_lats: np.ndarray, gt_lons: np.ndarray) -> np.ndarray:
    """Calculates point-wise position errors in meters."""
    errors = np.zeros(len(est_lats))
    for i in range(len(est_lats)):
        errors[i] = calculate_haversine_distance(est_lats[i], est_lons[i], gt_lats[i], gt_lons[i])
    return errors

def calculate_rmse(errors: np.ndarray) -> float:
    if len(errors) == 0:
        return 0.0
    return float(np.sqrt(np.mean(errors ** 2)))

def calculate_mae(errors: np.ndarray) -> float:
    if len(errors) == 0:
        return 0.0
    return float(np.mean(np.abs(errors)))

def calculate_max_error(errors: np.ndarray) -> float:
    if len(errors) == 0:
        return 0.0
    return float(np.max(errors))

def calculate_95th_percentile(errors: np.ndarray) -> float:
    if len(errors) == 0:
        return 0.0
    return float(np.percentile(errors, 95))

def calculate_drift_metrics(est_lats: np.ndarray, est_lons: np.ndarray, gt_lats: np.ndarray, gt_lons: np.ndarray) -> Dict[str, float]:
    """Calculates drift accumulation metrics for an outage segment."""
    if len(est_lats) < 2:
        return {"absolute_drift_m": 0.0, "drift_percent": 0.0, "total_distance_m": 0.0}
        
    # Total distance traveled according to ground truth
    total_dist = 0.0
    for i in range(1, len(gt_lats)):
        total_dist += calculate_haversine_distance(gt_lats[i-1], gt_lons[i-1], gt_lats[i], gt_lons[i])
        
    final_error = calculate_haversine_distance(est_lats[-1], est_lons[-1], gt_lats[-1], gt_lons[-1])
    
    drift_percent = (final_error / max(1.0, total_dist)) * 100.0
    
    return {
        "absolute_drift_m": float(final_error),
        "drift_percent": float(drift_percent),
        "total_distance_m": float(total_dist)
    }

def evaluate_trajectory(estimated: List[Dict[str, Any]], ground_truth: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Evaluates a full trajectory against ground truth.
    Assumes synchronized lists.
    """
    if not estimated or not ground_truth or len(estimated) != len(ground_truth):
        raise ValueError("Estimated and ground truth trajectories must be aligned and non-empty.")
        
    est_lats = np.array([pt['lat'] for pt in estimated])
    est_lons = np.array([pt['lon'] for pt in estimated])
    gt_lats = np.array([pt['lat'] for pt in ground_truth])
    gt_lons = np.array([pt['lon'] for pt in ground_truth])
    
    pos_errors = calculate_position_errors(est_lats, est_lons, gt_lats, gt_lons)
    
    est_speeds = np.array([pt.get('speed', 0.0) for pt in estimated])
    gt_speeds = np.array([pt.get('speed', 0.0) for pt in ground_truth])
    speed_errors = np.abs(est_speeds - gt_speeds)
    
    drift_metrics = calculate_drift_metrics(est_lats, est_lons, gt_lats, gt_lons)
    
    return {
        "position_rmse": calculate_rmse(pos_errors),
        "position_mae": calculate_mae(pos_errors),
        "position_max": calculate_max_error(pos_errors),
        "position_95th": calculate_95th_percentile(pos_errors),
        "speed_rmse": calculate_rmse(speed_errors),
        "absolute_drift_m": drift_metrics["absolute_drift_m"],
        "drift_percent": drift_metrics["drift_percent"],
        "total_distance_m": drift_metrics["total_distance_m"],
        "pointwise_pos_errors": pos_errors.tolist(),
        "pointwise_speed_errors": speed_errors.tolist()
    }
