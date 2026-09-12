import os
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Any

class BenchmarkPlotter:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def _save_plot(self, name: str):
        path = os.path.join(self.output_dir, f"{name}.png")
        plt.tight_layout()
        plt.savefig(path, dpi=300, bbox_inches='tight')
        plt.close()
        return path

    def plot_trajectories(self, ground_truth: List[Dict[str, Any]], configurations: Dict[str, List[Dict[str, Any]]], outage_mask: List[bool] = None) -> str:
        """Plots trajectories on an equal-aspect 2D plane."""
        plt.figure(figsize=(10, 10))
        
        gt_lats = [pt['lat'] for pt in ground_truth]
        gt_lons = [pt['lon'] for pt in ground_truth]
        
        plt.plot(gt_lons, gt_lats, 'k--', label='Ground Truth (GNSS)', linewidth=2, alpha=0.7)
        
        # Plot Outage Region if available
        if outage_mask and len(outage_mask) == len(ground_truth):
            outage_lats = [gt_lats[i] for i in range(len(gt_lats)) if outage_mask[i]]
            outage_lons = [gt_lons[i] for i in range(len(gt_lons)) if outage_mask[i]]
            if outage_lats:
                plt.scatter(outage_lons, outage_lats, c='red', s=10, alpha=0.3, label='GNSS Outage Window')
                
        colors = ['b', 'g', 'r', 'c', 'm', 'y', 'orange', 'purple']
        for i, (name, traj) in enumerate(configurations.items()):
            c = colors[i % len(colors)]
            t_lats = [pt['lat'] for pt in traj]
            t_lons = [pt['lon'] for pt in traj]
            plt.plot(t_lons, t_lats, label=name, color=c, linewidth=1.5, alpha=0.8)
            
        plt.title('Trajectory Comparison')
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        # Crucial: Equal scaling to accurately represent geometric distance
        plt.gca().set_aspect(1.0 / np.cos(np.mean(gt_lats) * np.pi / 180.0))
        plt.grid(True, linestyle=':', alpha=0.6)
        plt.legend()
        
        return self._save_plot('trajectory_comparison')
        
    def plot_drift_curves(self, times: List[float], errors_by_config: Dict[str, List[float]], outage_start: float = None, outage_end: float = None) -> str:
        """Plots position error vs time."""
        plt.figure(figsize=(12, 6))
        
        # Normalize times to start at 0
        t0 = times[0]
        norm_times = [t - t0 for t in times]
        
        if outage_start is not None and outage_end is not None:
            norm_start = outage_start - t0
            norm_end = outage_end - t0
            plt.axvspan(norm_start, norm_end, color='red', alpha=0.1, label='GNSS Outage')
            
        colors = ['b', 'g', 'r', 'c', 'm', 'y', 'orange', 'purple']
        for i, (name, errors) in enumerate(errors_by_config.items()):
            c = colors[i % len(colors)]
            plt.plot(norm_times, errors, label=name, color=c, linewidth=1.5)
            
        plt.title('Position Error (Drift) vs Time')
        plt.xlabel('Time (s)')
        plt.ylabel('Position Error (m)')
        plt.grid(True, linestyle=':', alpha=0.6)
        plt.legend()
        
        return self._save_plot('drift_curves')
