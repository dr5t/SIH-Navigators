import json
import torch
import torch.nn as nn
from ml.preprocessing.features import FeatureExtractor

def export_android_model(model: nn.Module, save_path: str, metadata_path: str, seq_len: int = 200):
    """
    Exports the PyTorch model to TorchScript for Android deployment.
    Also exports the EXACT normalization parameters and windowing metadata
    to ensure perfect parity between training and inference.
    """
    model.eval()
    dummy_input = torch.randn(1, 6, seq_len)
    traced_script_module = torch.jit.trace(model, dummy_input)
    traced_script_module.save(save_path)
    print(f"Exported TorchScript model to {save_path}")
    
    # Export Metadata for Parity
    fe = FeatureExtractor(seq_len=seq_len)
    metadata = {
        "seq_len": fe.seq_len,
        "stride": fe.stride,
        "channels": fe.channels,
        "normalization": {
            "accel_mean": fe.accel_mean.tolist(),
            "accel_std": fe.accel_std.tolist(),
            "gyro_mean": fe.gyro_mean.tolist(),
            "gyro_std": fe.gyro_std.tolist()
        },
        "output_unit": "m/s"
    }
    
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=4)
    print(f"Exported Model Metadata to {metadata_path}")
