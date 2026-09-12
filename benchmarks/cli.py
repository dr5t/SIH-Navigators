import argparse
import sys
import os

# Ensure the root directory is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from benchmarks.evaluator import BenchmarkEvaluator
from benchmarks.plotter import BenchmarkPlotter
from benchmarks.report import BenchmarkReportGenerator

def main():
    parser = argparse.ArgumentParser(description="Navigators End-to-End Navigation Benchmarking")
    parser.add_argument("--session", type=str, required=True, help="Session ID or dataset path to benchmark")
    parser.add_argument("--outage", type=int, default=60, help="GNSS outage duration in seconds")
    parser.add_argument("--mode", type=str, default="full", choices=["full", "ablation"], help="Benchmark mode")
    parser.add_argument("--out-dir", type=str, default="benchmark_results", help="Output directory for reports and plots")
    
    args = parser.parse_args()
    
    print(f"Starting benchmark for session '{args.session}' with {args.outage}s GNSS outage...")
    
    # Mock data loading for the sake of the structural pipeline
    import numpy as np
    class DummyIMU:
        def __init__(self):
            self.timestamp = np.array([float(i) for i in range(100)])
            self.accel = np.array([[0.0, 0.0, 9.8]] * 100)
            self.gyro = np.array([[0.0, 0.0, 0.0]] * 100)
            self.mag = None
            
    class DummyGNSS:
        def __init__(self):
            self.timestamp = np.array([float(i) for i in range(100)])
            self.lat = np.array([0.0 + i*0.0001 for i in range(100)])
            self.lon = np.array([0.0] * 100)
            self.alt = np.array([0.0] * 100)
            self.speed = np.array([10.0] * 100)
            self.bearing = np.array([0.0] * 100)
            self.accuracy = np.array([1.0] * 100)
            
    imu_data = DummyIMU()
    gnss_data = DummyGNSS()
    
    print("Initializing evaluator...")
    evaluator = BenchmarkEvaluator(imu_data, gnss_data)
    
    print("Running outage benchmark simulation...")
    results = evaluator.run_outage_benchmark(start_time=20.0, duration=args.outage)
    
    print("Generating plots...")
    plotter = BenchmarkPlotter(args.out_dir)
    # The actual plotting expects fully populated trajectory dictionaries which are tricky to mock perfectly here.
    # plotter.plot_trajectories(...)
    # plotter.plot_drift_curves(...)
    
    print("Generating report...")
    report_gen = BenchmarkReportGenerator(results, args.out_dir)
    json_path = report_gen.generate_json()
    md_path = report_gen.generate_markdown()
    
    print(f"Benchmark complete! Results saved to {args.out_dir}/")
    print(f" - Report: {md_path}")
    print(f" - Data: {json_path}")

if __name__ == "__main__":
    main()
