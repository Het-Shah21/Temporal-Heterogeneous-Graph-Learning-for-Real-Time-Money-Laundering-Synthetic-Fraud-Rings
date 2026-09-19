import os
import sys
import unittest
import shutil

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from xai.explainer import FraudExplainer
    from export.triton_exporter import TritonExporter
except ImportError:
    pass

class TestXAIAndExport(unittest.TestCase):
    def setUp(self):
        self.output_dir = os.path.join(os.path.dirname(__file__), 'test_triton_repo', '1')

    def test_triton_export(self):
        # Mock model
        model = None
        exporter = TritonExporter(model, self.output_dir)
        
        # Test export logic
        exporter.export_to_onnx()
        exporter.generate_config()
        
        # Assert files exist
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, 'model.onnx')))
        self.assertTrue(os.path.exists(os.path.join(os.path.dirname(self.output_dir), 'config.pbtxt')))

    def tearDown(self):
        if os.path.exists(os.path.dirname(self.output_dir)):
            shutil.rmtree(os.path.dirname(self.output_dir))

if __name__ == "__main__":
    unittest.main()
