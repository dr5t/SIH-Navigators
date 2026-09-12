import matplotlib.pyplot as plt
import pandas as pd

def plot_trajectory_comparison(ground_truth_df, estimated_df, title="Trajectory Comparison"):
    """
    Plots a 2D map comparing the ground truth GNSS trajectory and the estimated trajectory.
    Expects dataframes with 'lat' and 'lon'.
    """
    plt.figure(figsize=(10, 8))
    
    if ground_truth_df is not None and not ground_truth_df.empty:
        plt.plot(ground_truth_df['lon'], ground_truth_df['lat'], 
                 label='Ground Truth (GNSS)', color='blue', alpha=0.6, linewidth=2)
                 
    if estimated_df is not None and not estimated_df.empty:
        plt.plot(estimated_df['lon'], estimated_df['lat'], 
                 label='Estimated (DR)', color='red', alpha=0.8, linewidth=2, linestyle='--')
                 
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    return plt

def plot_error_over_time(timestamps, error_array, title="Position Error Over Time"):
    plt.figure(figsize=(10, 4))
    plt.plot(timestamps, error_array, color='red')
    plt.xlabel("Time")
    plt.ylabel("Error (meters)")
    plt.title(title)
    plt.grid(True)
    plt.tight_layout()
    return plt
