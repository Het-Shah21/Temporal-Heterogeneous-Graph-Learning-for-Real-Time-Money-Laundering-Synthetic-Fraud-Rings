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
            raise ImportError("PyTorch Geometric is required.")
            
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

        self.lin1 = Linear(hidden_channels * 2 + 2, hidden_channels)
        self.lin2 = Linear(hidden_channels, out_channels)

    def forward(self, x_dict, edge_index_dict, edge_attr_dict):
        x_dict = self.conv1(x_dict, edge_index_dict)
        x_dict = {key: F.relu(x) for key, x in x_dict.items()}
        x_dict = self.conv2(x_dict, edge_index_dict)
        
        src_idx, dst_idx = edge_index_dict[('account', 'sends', 'account')]
        
        src_emb = x_dict['account'][src_idx]
        dst_emb = x_dict['account'][dst_idx]
        edge_attr = edge_attr_dict[('account', 'sends', 'account')]
        
        edge_rep = torch.cat([src_emb, dst_emb, edge_attr], dim=1)
        
        out = F.relu(self.lin1(edge_rep))
        out = self.lin2(out)
        return out.squeeze(-1)

def get_criterion(data):
    mask = data['account', 'sends', 'account'].train_mask
    y_train = data['account', 'sends', 'account'].y[mask]
    num_pos = y_train.sum().item()
    num_neg = len(y_train) - num_pos
    weight = num_neg / num_pos if num_pos > 0 else 1.0
    return torch.nn.BCEWithLogitsLoss(pos_weight=torch.tensor([weight], dtype=torch.float))

def train_epoch(model, optimizer, loader, criterion, device):
    """HARDWARE LOGIC: Streams data through GPU in minibatches to prevent VRAM OOM crashes."""
    model.train()
    total_loss = 0
    batches = 0
    
    for batch in loader:
        batch = batch.to(device)
        optimizer.zero_grad()
        
        out = model(batch.x_dict, batch.edge_index_dict, batch.edge_attr_dict)
        
        mask = batch['account', 'sends', 'account'].train_mask
        if mask.sum() > 0:
            loss = criterion(out[mask], batch['account', 'sends', 'account'].y[mask])
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
            batches += 1
            
    return total_loss / max(1, batches)

def evaluate_model(model, loader, mask_name='test_mask', device='cpu'):
    """Evaluates metrics block-by-block, maintaining flat memory usage."""
    model.eval()
    all_y_true = []
    all_y_proba = []
    all_y_pred = []
    
    with torch.no_grad():
        for batch in loader:
            batch = batch.to(device)
            out = model(batch.x_dict, batch.edge_index_dict, batch.edge_attr_dict)
            mask = batch['account', 'sends', 'account'][mask_name]
            
            if mask.sum().item() > 0:
                y_true = batch['account', 'sends', 'account'].y[mask].cpu().numpy()
                y_logits = out[mask].cpu().numpy()
                
                y_proba = 1.0 / (1.0 + np.exp(-y_logits))
                y_pred = (y_proba > 0.5).astype(int)
                
                all_y_true.extend(y_true)
                all_y_proba.extend(y_proba)
                all_y_pred.extend(y_pred)
                
    if len(all_y_true) == 0:
        return 0.0, 0.0
        
    y_true_arr = np.array(all_y_true)
    y_proba_arr = np.array(all_y_proba)
    y_pred_arr = np.array(all_y_pred)
    
    if len(np.unique(y_true_arr)) > 1:
        auc = roc_auc_score(y_true_arr, y_proba_arr)
    else:
        auc = 0.5
        
    f1 = f1_score(y_true_arr, y_pred_arr, zero_division=0)
    report = classification_report(y_true_arr, y_pred_arr, target_names=["Legitimate", "Fraud"], zero_division=0)
    
    print(f"\n--- GNN METRICS ({mask_name.upper()}) ---")
    print(f"ROC-AUC: {auc:.4f}")
    print(f"F1-Score: {f1:.4f}")
    print("\nClassification Report:\n", report)
    
    # Explicit memory flush
    del all_y_true, all_y_proba, all_y_pred
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        
    return auc, f1
