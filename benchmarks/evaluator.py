import os
from typing import Dict, Any, List
from replay.engine import ReplayEngine
from replay.gnss_blackout import inject_gnss_blackout
from benchmarks.metrics import evaluate_trajectory
from navigation_core.engine import NavigationEngine

class BenchmarkConfig:
    def __init__(self, name: str, enable_vehicle_constraints: bool = False, enable_ai_speed: bool = False, enable_map_matching: bool = False):
        self.name = name
        self.enable_vehicle_constraints = enable_vehicle_constraints
        self.enable_ai_speed = enable_ai_speed
        self.enable_map_matching = enable_map_matching

class BenchmarkEvaluator:
    def __init__(self, imu_data, gnss_data):
        self.imu_data = imu_data
        self.gnss_data = gnss_data
        self.configurations = [
            BenchmarkConfig("B. Pure INS", False, False, False),
            BenchmarkConfig("C. INS + NHC", True, False, False),
            BenchmarkConfig("D. INS + NHC + AI", True, True, False),
            BenchmarkConfig("E. INS + NHC + AI + Map", True, True, True)
        ]
        
    def _create_engine(self, config: BenchmarkConfig) -> NavigationEngine:
        # In reality, this would configure the NavigationEngine flags
        # Currently, NavigationEngine always runs full configuration, so we must mock or patch it for ablation
        engine = NavigationEngine(ref_lat=0.0, ref_lon=0.0, ref_alt=0.0)
        
        # Disable features for ablation
        if not config.enable_vehicle_constraints:
            engine.nhc = None # Or provide a dummy
            
        if not config.enable_ai_speed:
            engine.ai_speed_estimator = None
            
        if not config.enable_map_matching:
            engine.map_matcher = None
            
        return engine

    def run_outage_benchmark(self, start_time: float, duration: float) -> Dict[str, Any]:
        """Runs the benchmark suite for a specific simulated outage."""
        available_gnss, ground_truth = inject_gnss_blackout(self.gnss_data, start_time, duration)
        
        results = {
            "outage_start": start_time,
            "outage_duration": duration,
            "ground_truth": ground_truth,
            "configurations": {}
        }
        
        for config in self.configurations:
            engine = self._create_engine(config)
            trajectory = []
            
            def nav_callback(imu_sample, gnss):
                # Only feed GNSS if it is outside the blackout window
                ts = imu_sample['timestamp']
                
                # Check for available GNSS
                # Simple logic for replay: if ts matches an available GNSS ts, feed it
                # For this benchmark framework, we'll just simulate pushing IMU and GNSS
                pass
                
            # Run replay engine
            replay = ReplayEngine(self.imu_data, available_gnss, nav_callback)
            replay.play(speed=0) # Run as fast as possible
            
            # Since the real replay logic would be complex to fully implement here in a dummy script,
            # we'll assume `trajectory` gets populated with state dicts.
            
            # evaluate_trajectory(trajectory, ground_truth)
            results["configurations"][config.name] = {
                "trajectory": trajectory,
                "metrics": {} # populate with metrics
            }
            
        return results
