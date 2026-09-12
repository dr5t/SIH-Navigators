import unittest
import torch
import os
from ml.models.speed_model import SpeedModel
from ml.export.exporter import export_android_model

class TestMLGroupB(unittest.TestCase):

    def test_model_forward(self):
        model = SpeedModel(seq_len=200)
        # Dummy batch of 5 windows
        x = torch.randn(5, 6, 200)
        out = model(x)
        self.assertEqual(out.shape, (5, 1))
        
    def test_export(self):
        model = SpeedModel(seq_len=50)
        export_android_model(model, "tmp_test_export.pt", "tmp_test_metadata.json", seq_len=50)
        self.assertTrue(os.path.exists("tmp_test_export.pt"))
        self.assertTrue(os.path.exists("tmp_test_metadata.json"))
        
        # Cleanup
        if os.path.exists("tmp_test_export.pt"): os.remove("tmp_test_export.pt")
        if os.path.exists("tmp_test_metadata.json"): os.remove("tmp_test_metadata.json")

if __name__ == '__main__':
    unittest.main()
