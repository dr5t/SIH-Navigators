import numpy as np
from benchmarks.metrics import (
    calculate_haversine_distance, 
    calculate_rmse, 
    calculate_drift_metrics,
    evaluate_trajectory
)

def test_haversine():
    # Test known distance: 1 deg lat is approx 111km
    d = calculate_haversine_distance(0.0, 0.0, 1.0, 0.0)
    assert 110000 < d < 112000

def test_rmse():
    errors = np.array([3.0, 4.0])
    # mean of sq = (9 + 16)/2 = 12.5 -> sqrt(12.5) ~ 3.535
    rmse = calculate_rmse(errors)
    assert abs(rmse - np.sqrt(12.5)) < 1e-5

def test_drift_metrics():
    # Ground truth: moves 0.001 deg lat (approx 111m)
    # Estimated: moves only 0.0005 deg lat
    
    gt_lats = np.array([0.0, 0.001])
    gt_lons = np.array([0.0, 0.0])
    
    est_lats = np.array([0.0, 0.0005])
    est_lons = np.array([0.0, 0.0])
    
    metrics = calculate_drift_metrics(est_lats, est_lons, gt_lats, gt_lons)
    
    total_dist = metrics["total_distance_m"]
    abs_drift = metrics["absolute_drift_m"]
    
    assert 110 < total_dist < 112 # ~111m
    assert 55 < abs_drift < 56    # ~55.5m error at end
    
    drift_percent = metrics["drift_percent"]
    assert abs(drift_percent - 50.0) < 1.0 # 50% drift
    
def test_evaluate_trajectory():
    gt = [
        {"lat": 0.0, "lon": 0.0, "speed": 10.0},
        {"lat": 0.001, "lon": 0.0, "speed": 10.0}
    ]
    est = [
        {"lat": 0.0, "lon": 0.0, "speed": 10.0},
        {"lat": 0.0005, "lon": 0.0, "speed": 8.0}
    ]
    
    results = evaluate_trajectory(est, gt)
    assert abs(results["speed_rmse"] - np.sqrt(2)) < 1e-5
