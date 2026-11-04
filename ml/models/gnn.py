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
            ('account', 'uses', 'device'): SAGEConv((-1, -1), hidden_channels),
            ('account', 'logs_in', 'ip'): SAGEConv((-1, -1), hidden_channels),
        }, aggr='sum')
        
        self.conv2 = HeteroConv({
            ('account', 'sends', 'account'): SAGEConv((-1, -1), hidden_channels),
            ('account', 'uses', 'device'): SAGEConv((-1, -1), hidden_channels),
            ('account', 'logs_in', 'ip'): SAGEConv((-1, -1), hidden_channels),
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

class FocalLoss(torch.nn.Module):
    def __init__(self, alpha=0.25, gamma=2.0, reduction='mean'):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.reduction = reduction

    def forward(self, inputs, targets):
        bce_loss = F.binary_cross_entropy_with_logits(inputs, targets, reduction='none')
        pt = torch.exp(-bce_loss) 
        focal_loss = self.alpha * (1 - pt) ** self.gamma * bce_loss
        
        if self.reduction == 'mean':
            return focal_loss.mean()
        elif self.reduction == 'sum':
            return focal_loss.sum()
        return focal_loss

def get_criterion(data):
    mask = data['account', 'sends', 'account'].train_mask
    y_train = data['account', 'sends', 'account'].y[mask]
    num_pos = y_train.sum().item()
    num_neg = len(y_train) - num_pos
    weight = num_neg / num_pos if num_pos > 0 else 1.0
    return torch.nn.BCEWithLogitsLoss(pos_weight=torch.tensor([weight], dtype=torch.float))

def train_epoch(model, optimizer, data, criterion, device):
    """HARDWARE LOGIC: Full-batch training since we forced HI-Small_Trans.csv (<1GB VRAM)."""
    model.train()
    
    data = data.to(device)
    optimizer.zero_grad()
    
    out = model(data.x_dict, data.edge_index_dict, data.edge_attr_dict)
    
    mask = data['account', 'sends', 'account'].train_mask
    if mask.sum() > 0:
        loss = criterion(out[mask], data['account', 'sends', 'account'].y[mask])
        loss.backward()
        optimizer.step()
        return loss.item()
        
    return 0.0

def evaluate_model(model, data, mask_name='test_mask', device='cpu', threshold=0.5, tune_threshold=False):
    """Evaluates metrics in full-batch mode. Optionally tunes the decision threshold."""
    model.eval()
    all_y_true = []
    all_y_proba = []
    
    with torch.no_grad():
        data = data.to(device)
        out = model(data.x_dict, data.edge_index_dict, data.edge_attr_dict)
        mask = data['account', 'sends', 'account'][mask_name]
        
        if mask.sum().item() > 0:
            y_true = data['account', 'sends', 'account'].y[mask].cpu().numpy()
            y_logits = out[mask].cpu().numpy()
            
            y_proba = 1.0 / (1.0 + np.exp(-y_logits))
            
            all_y_true.extend(y_true)
            all_y_proba.extend(y_proba)
            
    if len(all_y_true) == 0:
        return 0.0, 0.0, threshold
        
    y_true_arr = np.array(all_y_true)
    y_proba_arr = np.array(all_y_proba)
    
    if len(np.unique(y_true_arr)) > 1:
        auc = roc_auc_score(y_true_arr, y_proba_arr)
    else:
        auc = 0.5
        
    best_threshold = threshold
    if tune_threshold:
        # Sweep thresholds to maximize F1-Score
        thresholds = np.linspace(0.1, 0.95, 85)
        best_f1 = 0
        for t in thresholds:
            preds = (y_proba_arr > t).astype(int)
            f1 = f1_score(y_true_arr, preds, zero_division=0)
            if f1 > best_f1:
                best_f1 = f1
                best_threshold = t
        print(f"\n[Optimal Threshold Tuned to: {best_threshold:.4f} (F1: {best_f1:.4f})]")
        
    y_pred_arr = (y_proba_arr > best_threshold).astype(int)
    f1 = f1_score(y_true_arr, y_pred_arr, zero_division=0)
    report = classification_report(y_true_arr, y_pred_arr, target_names=["Legitimate", "Fraud"], zero_division=0)
    
    print(f"\n--- GNN METRICS ({mask_name.upper()}) ---")
    print(f"ROC-AUC: {auc:.4f}")
    print(f"F1-Score: {f1:.4f} (Threshold: {best_threshold:.4f})")
    print("\nClassification Report:\n", report)
    
    # Explicit memory flush
    del all_y_true, all_y_proba
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        
    return auc, f1, best_threshold
