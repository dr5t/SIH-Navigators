import torch
import numpy as np
from ml.models.speed_model import SpeedModel
from ml.export.exporter import export_android_model

def verify_numerical_parity():
    print("Verifying Training/Inference Numerical Parity...")
    
    # 1. Initialize PyTorch model and put it in eval mode
    model = SpeedModel(seq_len=200)
    model.eval()
    
    # 2. Create a dummy test window (e.g. from FeatureExtractor)
    dummy_window = np.random.randn(1, 6, 200).astype(np.float32)
    input_tensor = torch.from_numpy(dummy_window)
    
    # 3. Get reference prediction
    with torch.no_grad():
        reference_pred = model(input_tensor).numpy()[0, 0]
        
    # 4. Export it
    export_android_model(model, "test_export.pt", "test_metadata.json")
    
    # 5. Load TorchScript exported model (Simulating Android inference)
    exported_model = torch.jit.load("test_export.pt")
    exported_model.eval()
    
    with torch.no_grad():
        exported_pred = exported_model(input_tensor).numpy()[0, 0]
        
    # 6. Compare
    diff = abs(reference_pred - exported_pred)
    
    print(f"Reference Prediction: {reference_pred:.6f}")
    print(f"Exported Prediction:  {exported_pred:.6f}")
    print(f"Absolute Difference:  {diff:.10f}")
    
    assert diff < 1e-5, f"Numerical Parity FAILED! Difference: {diff}"
    print("Numerical Parity Passed!")
    
if __name__ == "__main__":
    verify_numerical_parity()
