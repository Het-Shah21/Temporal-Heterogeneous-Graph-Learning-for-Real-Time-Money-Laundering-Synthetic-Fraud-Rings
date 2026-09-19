import pandas as pd
import numpy as np
import os
import shutil
import unittest
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from models.baseline import BaselineModel

class TestBaselineModel(unittest.TestCase):
    def setUp(self):
        self.proc_dir = os.path.join(os.path.dirname(__file__), 'test_processed')
        self.art_dir = os.path.join(os.path.dirname(__file__), 'test_artifacts')
        os.makedirs(self.proc_dir, exist_ok=True)
        
        # Create 100 Dummy Transactions
        np.random.seed(42)
        data = {
            'src': np.random.choice(['A1', 'A2', 'A3', 'A4', 'A5'], 100),
            'dst': np.random.choice(['A1', 'A2', 'A3', 'A4', 'A5'], 100),
            'amount': np.random.uniform(10, 1000, 100),
            'timestamp': sorted(np.random.randint(1000, 5000, 100)),
            'label': np.random.choice([0, 1], 100, p=[0.9, 0.1])
        }
        self.dummy_csv = os.path.join(self.proc_dir, 'edges_sends.csv')
        pd.DataFrame(data).to_csv(self.dummy_csv, index=False)

    def test_baseline_training(self):
        baseline = BaselineModel(self.dummy_csv, self.art_dir)
        baseline.train_and_evaluate()
        
        self.assertTrue(os.path.exists(os.path.join(self.art_dir, 'baseline_xgboost.json')))
        self.assertTrue(os.path.exists(os.path.join(self.art_dir, 'baseline_metrics.json')))

    def tearDown(self):
        shutil.rmtree(self.proc_dir)
        if os.path.exists(self.art_dir):
            shutil.rmtree(self.art_dir)

if __name__ == "__main__":
    unittest.main()
