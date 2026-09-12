import numpy as np


class KinematicBaseline:
    """
    A simple baseline that integrates forward acceleration to estimate speed.
    Assuming the device is relatively aligned such that Accel X is forward.
    """
    def __init__(self, dt: float = 0.01):
        self.dt = dt
        
    def predict(self, accel_windows: np.ndarray) -> np.ndarray:
        """
        accel_windows: shape (Batch, SeqLen, Channels)
        Assuming channel 0 is forward accel.
        """
        batch_size, seq_len, _ = accel_windows.shape
        predictions = np.zeros(batch_size)
        
        for i in range(batch_size):
            # Integrate forward acceleration over the window
            forward_accel = accel_windows[i, :, 0]
            
            # Simple Euler integration (assuming starting speed is 0 for the window)
            # This is a very weak baseline, but serves its purpose.
            speed = np.sum(forward_accel) * self.dt
            predictions[i] = max(0.0, speed) # Speed >= 0
            
        return predictions

def evaluate_baseline(predictions: np.ndarray, targets: np.ndarray):
    if len(targets) == 0:
        print("No data to evaluate.")
        return
        
    mae = np.mean(np.abs(targets - predictions))
    rmse = np.sqrt(np.mean((targets - predictions)**2))
    
    print("\n--- Baseline Metrics ---")
    print(f"MAE:  {mae:.2f} m/s")
    print(f"RMSE: {rmse:.2f} m/s")
    print("------------------------\n")
