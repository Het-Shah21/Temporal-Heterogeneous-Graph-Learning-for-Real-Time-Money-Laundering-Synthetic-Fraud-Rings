import os
import sys
import torch
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from torch_geometric.data import HeteroData
    from models.gnn import HeteroFraudGNN, train_epoch, get_criterion, evaluate_model
    HAS_PYG = True
except ImportError:
    HAS_PYG = False

class TestGNN(unittest.TestCase):
    @unittest.skipIf(not HAS_PYG, "PyTorch Geometric is not installed.")
    def test_gnn_forward_pass(self):
        # 1. Create a tiny mock HeteroData graph
        data = HeteroData()
        
        # 5 accounts, 2 devices, 2 ips
        data['account'].x = torch.rand((5, 3))
        data['device'].x = torch.rand((2, 1))
        data['ip'].x = torch.rand((2, 1))
        
        # Edges
        # Account -> Sends -> Account
        data['account', 'sends', 'account'].edge_index = torch.tensor([[0, 1, 2, 3], [1, 2, 3, 4]], dtype=torch.long)
        data['account', 'sends', 'account'].edge_attr = torch.rand((4, 2))
        data['account', 'sends', 'account'].y = torch.tensor([0.0, 1.0, 0.0, 0.0])
        data['account', 'sends', 'account'].train_mask = torch.tensor([True, True, False, False])
        
        # Account -> Uses -> Device
        data['account', 'uses', 'device'].edge_index = torch.tensor([[0, 1, 2, 3, 4], [0, 0, 1, 1, 1]], dtype=torch.long)
        
        # Account -> Logs_in -> IP
        data['account', 'logs_in', 'ip'].edge_index = torch.tensor([[0, 1, 2, 3, 4], [0, 1, 1, 0, 0]], dtype=torch.long)
        
        # 2. Initialize Model
        hidden_channels = 16
        out_channels = 1
        model = HeteroFraudGNN(hidden_channels, out_channels)
        
        # 3. Test Forward Pass
        out = model(data.x_dict, data.edge_index_dict, data.edge_attr_dict)
        
        self.assertEqual(out.shape, (4,), "Output should match the number of 'sends' edges (4).")
        self.assertTrue(torch.is_tensor(out))
        
        # 4. Test Train Epoch & get_criterion
        optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
        criterion = get_criterion(data)
        
        initial_loss = train_epoch(model, optimizer, data, criterion)
        self.assertIsInstance(initial_loss, float)
        self.assertGreater(initial_loss, 0.0)
        
        # 5. Test Evaluate Loop
        data['account', 'sends', 'account'].test_mask = torch.tensor([False, False, True, True])
        auc, f1 = evaluate_model(model, data, mask_name='test_mask')
        self.assertIsInstance(auc, float)
        self.assertIsInstance(f1, float)

if __name__ == "__main__":
    unittest.main()
