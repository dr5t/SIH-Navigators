import json
import os
from datetime import datetime
from typing import Dict, Any

class BenchmarkReportGenerator:
    def __init__(self, results: Dict[str, Any], output_dir: str):
        self.results = results
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def generate_json(self) -> str:
        path = os.path.join(self.output_dir, "benchmark_results.json")
        
        # Clean up numpy arrays for JSON serialization
        clean_results = self._clean_dict(self.results)
        
        with open(path, 'w') as f:
            json.dump(clean_results, f, indent=4)
        return path
        
    def _clean_dict(self, d: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively convert numpy types to standard python types for JSON."""
        clean = {}
        for k, v in d.items():
            if isinstance(v, dict):
                clean[k] = self._clean_dict(v)
            elif hasattr(v, 'tolist'): # numpy array
                clean[k] = v.tolist()
            elif hasattr(v, '__dict__'):
                # Handle objects like GnssData by skipping them or stringifying
                clean[k] = "<object data omitted>"
            else:
                clean[k] = v
        return clean

    def generate_markdown(self) -> str:
        path = os.path.join(self.output_dir, "benchmark_report.md")
        
        md = []
        md.append(f"# Navigators Navigation Engine Benchmark Report")
        md.append(f"**Date:** {datetime.now().isoformat()}")
        md.append("")
        
        md.append("## Executive Summary")
        md.append("This report evaluates the performance of the Navigators navigation engine during simulated GNSS outages.")
        md.append("")
        
        md.append("## Test Configuration")
        md.append(f"- **Outage Duration:** {self.results.get('outage_duration', 'Unknown')} seconds")
        md.append("")
        
        md.append("## Ablation Results")
        md.append("| Configuration | Absolute Drift (m) | Drift % | Position RMSE (m) | Max Error (m) |")
        md.append("|---|---|---|---|---|")
        
        configs = self.results.get('configurations', {})
        for name, config_data in configs.items():
            metrics = config_data.get('metrics', {})
            md.append(f"| {name} | {metrics.get('absolute_drift_m', 0):.2f} | {metrics.get('drift_percent', 0):.2f}% | {metrics.get('position_rmse', 0):.2f} | {metrics.get('position_max', 0):.2f} |")
            
        md.append("")
        md.append("## Trajectory Plots")
        md.append("![Trajectory Comparison](trajectory_comparison.png)")
        md.append("")
        md.append("## Error Plots")
        md.append("![Drift Curves](drift_curves.png)")
        
        with open(path, 'w') as f:
            f.write('\n'.join(md))
            
        return path
