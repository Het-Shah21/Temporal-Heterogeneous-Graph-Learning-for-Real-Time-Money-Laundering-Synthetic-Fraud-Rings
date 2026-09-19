import pandas as pd
import os
import shutil
import unittest
from hetero_builder import HeteroGraphBuilder

class TestHeteroGraphBuilder(unittest.TestCase):
    def setUp(self):
        self.raw_dir = os.path.join(os.path.dirname(__file__), 'test_raw')
        self.proc_dir = os.path.join(os.path.dirname(__file__), 'test_processed')
        os.makedirs(self.raw_dir, exist_ok=True)
        
        # Create Dummy Data
        data = {
            'Timestamp': [1, 2, 3, 4],
            'From_Account': ['A1', 'A2', 'A3', 'A4'],
            'To_Account': ['A2', 'A3', 'A1', 'A5'], # Cycle A1->A2->A3->A1
            'Amount_Received': [100.0, 95.0, 90.0, 50.0],
            'Is_Laundering': [0, 1, 1, 0] # A2, A3 involved in laundering
        }
        self.dummy_csv = os.path.join(self.raw_dir, 'dummy_txns.csv')
        pd.DataFrame(data).to_csv(self.dummy_csv, index=False)

    def test_hetero_graph_construction(self):
        builder = HeteroGraphBuilder(self.dummy_csv, self.proc_dir)
        builder.process()

        # Verify output files exist
        self.assertTrue(os.path.exists(os.path.join(self.proc_dir, 'nodes_account.csv')))
        self.assertTrue(os.path.exists(os.path.join(self.proc_dir, 'nodes_device.csv')))
        self.assertTrue(os.path.exists(os.path.join(self.proc_dir, 'edges_uses.csv')))
        
        # Verify laundering logic (shared device)
        uses_df = pd.read_csv(os.path.join(self.proc_dir, 'edges_uses.csv'))
        
        # A2 sent to A3 (Is_Laundering = 1). A3 should share A2's device.
        a2_device = uses_df[uses_df['src'] == 'A2']['dst'].values[0]
        a3_device = uses_df[uses_df['src'] == 'A3']['dst'].values[0]
        self.assertEqual(a2_device, a3_device, "Laundering accounts must share the same device.")

    def tearDown(self):
        shutil.rmtree(self.raw_dir)
        if os.path.exists(self.proc_dir):
            shutil.rmtree(self.proc_dir)

if __name__ == "__main__":
    unittest.main()
