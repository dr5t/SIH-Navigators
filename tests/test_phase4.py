import unittest
import torch
import os
from ml.models.speed_model import SpeedModel, export_torchscript

class TestPhase4(unittest.TestCase):
    def test_model_forward(self):
        model = SpeedModel(seq_len=200)
        x = torch.randn(2, 6, 200)  # Batch 2, 6 channels, 200 length
        out = model(x)
        self.assertEqual(out.shape, (2, 1))

    def test_torchscript_export(self):
        model = SpeedModel(seq_len=200)
        export_path = "test_speed_model.pt"
        export_torchscript(model, export_path)
        
        self.assertTrue(os.path.exists(export_path))
        
        # Load and verify
        loaded = torch.jit.load(export_path)
        x = torch.randn(1, 6, 200)
        with torch.no_grad():
            out1 = model(x)
            out2 = loaded(x)
            
        torch.testing.assert_close(out1, out2)
        os.remove(export_path)

if __name__ == '__main__':
    unittest.main()
