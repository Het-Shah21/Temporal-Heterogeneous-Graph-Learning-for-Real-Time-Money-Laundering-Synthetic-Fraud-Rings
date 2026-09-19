import torch
import torch.nn.functional as F
try:
    from torch_geometric.nn import SAGEConv, HeteroConv, Linear
except ImportError:
    SAGEConv = HeteroConv = Linear = None

class HeteroFraudGNN(torch.nn.Module):
    def __init__(self, hidden_channels, out_channels):
        super().__init__()
        if HeteroConv is None:
            raise ImportError("PyTorch Geometric is required to run the GNN.")
            
        # Graph Convolution Layers (Heterogeneous)
        # Using SAGEConv because it aggregates neighborhood features scalably
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
        # Shapes: hidden_channels + hidden_channels + 1 (amount)
        self.lin1 = Linear(hidden_channels * 2 + 1, hidden_channels)
        self.lin2 = Linear(hidden_channels, out_channels)

    def forward(self, x_dict, edge_index_dict, edge_attr_dict):
        # 1. Message Passing Phase (Updating Node Embeddings)
        x_dict = self.conv1(x_dict, edge_index_dict)
        x_dict = {key: F.relu(x) for key, x in x_dict.items()}
        x_dict = self.conv2(x_dict, edge_index_dict)
        
        # 2. Edge Classification Phase (Predicting on 'sends' edges)
        src_idx, dst_idx = edge_index_dict[('account', 'sends', 'account')]
        
        src_emb = x_dict['account'][src_idx]
        dst_emb = x_dict['account'][dst_idx]
        edge_attr = edge_attr_dict[('account', 'sends', 'account')]
        
        # Concat sender, receiver, and transaction amount
        edge_rep = torch.cat([src_emb, dst_emb, edge_attr], dim=1)
        
        # Pass through final MLP to get fraud probability logits
        out = F.relu(self.lin1(edge_rep))
        out = self.lin2(out)
        
        return out.squeeze(-1) # Logits for BCEWithLogitsLoss

def train_epoch(model, optimizer, data, criterion):
    model.train()
    optimizer.zero_grad()
    
    # Forward pass
    out = model(data.x_dict, data.edge_index_dict, data.edge_attr_dict)
    
    # Calculate loss only on the training mask
    mask = data['account', 'sends', 'account'].train_mask
    loss = criterion(out[mask], data['account', 'sends', 'account'].y[mask])
    
    loss.backward()
    optimizer.step()
    return loss.item()
