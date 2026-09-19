import torch
import torch.nn.functional as F
import numpy as np
from sklearn.metrics import classification_report, roc_auc_score, f1_score
try:
    from torch_geometric.nn import SAGEConv, HeteroConv, Linear
except ImportError:
    SAGEConv = HeteroConv = Linear = None

class HeteroFraudGNN(torch.nn.Module):
    def __init__(self, hidden_channels, out_channels):
        super().__init__()
        if HeteroConv is None:
            raise ImportError("PyTorch Geometric is required to run the GNN.")
            
        self.conv1 = HeteroConv({
            ('account', 'sends', 'account'): SAGEConv((-1, -1), hidden_channels),
            ('account', 'uses', 'device'): SAGEConv((-1, -1), hidden_channels, add_self_loops=False),
            ('account', 'logs_in', 'ip'): SAGEConv((-1, -1), hidden_channels, add_self_loops=False),
        }, aggr='sum')
        
        self.conv2 = HeteroConv({
            ('account', 'sends', 'account'): SAGEConv((-1, -1), hidden_channels),
            ('account', 'uses', 'device'): SAGEConv((-1, -1), hidden_channels, add_self_loops=False),
            ('account', 'logs_in', 'ip'): SAGEConv((-1, -1), hidden_channels, add_self_loops=False),
        }, aggr='sum')

        # Edge Classification MLP
        # Input: concat(src_account_emb, dst_account_emb, edge_features)
        # Shapes: hidden_channels + hidden_channels + 2 (amount, time_delta)
        self.lin1 = Linear(hidden_channels * 2 + 2, hidden_channels)
        self.lin2 = Linear(hidden_channels, out_channels)

    def forward(self, x_dict, edge_index_dict, edge_attr_dict):
        # 1. Message Passing Phase
        x_dict = self.conv1(x_dict, edge_index_dict)
        x_dict = {key: F.relu(x) for key, x in x_dict.items()}
        x_dict = self.conv2(x_dict, edge_index_dict)
        
        # 2. Edge Classification Phase
        src_idx, dst_idx = edge_index_dict[('account', 'sends', 'account')]
        
        src_emb = x_dict['account'][src_idx]
        dst_emb = x_dict['account'][dst_idx]
        edge_attr = edge_attr_dict[('account', 'sends', 'account')]
        
        edge_rep = torch.cat([src_emb, dst_emb, edge_attr], dim=1)
        
        out = F.relu(self.lin1(edge_rep))
        out = self.lin2(out)
        
        return out.squeeze(-1)

def get_criterion(data):
    """Calculates dynamic pos_weight for BCE loss to handle extreme fraud imbalance."""
    mask = data['account', 'sends', 'account'].train_mask
    y_train = data['account', 'sends', 'account'].y[mask]
    
    num_pos = y_train.sum().item()
    num_neg = len(y_train) - num_pos
    
    # scale_pos_weight = neg / pos
    weight = num_neg / num_pos if num_pos > 0 else 1.0
    pos_weight = torch.tensor([weight], dtype=torch.float)
    
    return torch.nn.BCEWithLogitsLoss(pos_weight=pos_weight)

def train_epoch(model, optimizer, data, criterion):
    model.train()
    optimizer.zero_grad()
    
    out = model(data.x_dict, data.edge_index_dict, data.edge_attr_dict)
    
    mask = data['account', 'sends', 'account'].train_mask
    loss = criterion(out[mask], data['account', 'sends', 'account'].y[mask])
    
    loss.backward()
    optimizer.step()
    return loss.item()

def evaluate_model(model, data, mask_name='test_mask'):
    """Evaluates the model and prints scientific metrics against the baseline."""
    model.eval()
    with torch.no_grad():
        out = model(data.x_dict, data.edge_index_dict, data.edge_attr_dict)
        mask = data['account', 'sends', 'account'][mask_name]
        
        # Ensure we have predictions to evaluate
        if mask.sum().item() == 0:
            return 0.0, 0.0
            
        y_true = data['account', 'sends', 'account'].y[mask].cpu().numpy()
        y_logits = out[mask].cpu().numpy()
        
        # Sigmoid for probabilities
        y_proba = 1.0 / (1.0 + np.exp(-y_logits))
        y_pred = (y_proba > 0.5).astype(int)
        
        # Handle cases where only one class is present in the split (unit testing)
        if len(np.unique(y_true)) > 1:
            auc = roc_auc_score(y_true, y_proba)
        else:
            auc = 0.5
            
        f1 = f1_score(y_true, y_pred, zero_division=0)
        report = classification_report(y_true, y_pred, zero_division=0)
        
        print(f"\n--- GNN METRICS ({mask_name.upper()}) ---")
        print(f"ROC-AUC: {auc:.4f}")
        print(f"F1-Score: {f1:.4f}")
        print("\nClassification Report:\n", report)
        
        return auc, f1
