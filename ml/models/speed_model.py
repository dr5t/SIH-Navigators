import torch
import torch.nn as nn

class SpeedModel(nn.Module):
    """
    1D-CNN to estimate forward speed from a window of IMU data.
    Input: (Batch, Channels=6, SeqLen) -> Accel (3), Gyro (3)
    Output: (Batch, 1) -> Forward speed (m/s)
    """
    def __init__(self, seq_len: int = 200):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv1d(6, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool1d(2),
            nn.Conv1d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool1d(1),
            nn.Flatten(),
            nn.Linear(64, 1)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)

def export_torchscript(model: nn.Module, save_path: str, seq_len: int = 200):
    """Exports model for Android deployment."""
    model.eval()
    dummy_input = torch.randn(1, 6, seq_len)
    traced_script_module = torch.jit.trace(model, dummy_input)
    traced_script_module.save(save_path)
