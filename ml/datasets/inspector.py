import os
import numpy as np
from ml.datasets.io_vnbd import list_sessions, IOVNBDParser

def inspect_dataset(base_dir: str = "ml/data/io_vnbd"):
    print(f"Inspecting IO-VNBD dataset in {base_dir}...")
    
    if not os.path.exists(base_dir):
        print("\n==================================================")
        print("CRITICAL: IO-VNBD DATASET NOT FOUND")
        print("==================================================")
        print(f"The directory {base_dir} does not exist.")
        print("Please supply the raw dataset to proceed with training.")
        return
        
    sessions = list_sessions(base_dir)
    if not sessions:
        print(f"No valid session directories found in {base_dir}.")
        return
        
    print(f"Found {len(sessions)} valid session(s).")
    
    total_duration = 0.0
    total_imu_samples = 0
    total_gnss_samples = 0
    
    for session in sessions:
        print(f"\n--- Session: {os.path.basename(session)} ---")
        parser = IOVNBDParser(session)
        
        try:
            imu, gnss = parser.load_all()
            
            # IMU Stats
            imu_duration = imu.timestamp[-1] - imu.timestamp[0] if len(imu.timestamp) > 0 else 0
            imu_freq = len(imu.timestamp) / imu_duration if imu_duration > 0 else 0
            
            # GNSS Stats
            gnss_duration = gnss.timestamp[-1] - gnss.timestamp[0] if len(gnss.timestamp) > 0 else 0
            gnss_freq = len(gnss.timestamp) / gnss_duration if gnss_duration > 0 else 0
            
            print(f"IMU:  {len(imu.timestamp)} samples, ~{imu_freq:.1f} Hz, duration {imu_duration:.1f}s")
            print(f"GNSS: {len(gnss.timestamp)} samples, ~{gnss_freq:.1f} Hz, duration {gnss_duration:.1f}s")
            
            # Sanity checks
            if len(imu.timestamp) > 1 and not np.all(np.diff(imu.timestamp) > 0):
                print("  WARNING: Non-monotonic timestamps found in IMU!")
                
            if len(gnss.timestamp) > 1 and not np.all(np.diff(gnss.timestamp) > 0):
                print("  WARNING: Non-monotonic timestamps found in GNSS!")
                
            total_duration += imu_duration
            total_imu_samples += len(imu.timestamp)
            total_gnss_samples += len(gnss.timestamp)
            
        except Exception as e:
            print(f"  ERROR loading session: {e}")
            
    print("\n==================================================")
    print("DATASET SUMMARY")
    print("==================================================")
    print(f"Total Sessions: {len(sessions)}")
    print(f"Total IMU Samples: {total_imu_samples}")
    print(f"Total GNSS Samples: {total_gnss_samples}")
    print(f"Total Duration: {total_duration/60.0:.1f} minutes")

if __name__ == "__main__":
    inspect_dataset()
