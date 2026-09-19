import os
import pandas as pd
try:
    import torch
    from torch_geometric.data import HeteroData
except ImportError:
    torch = None
    HeteroData = None
    print("Warning: PyTorch Geometric is not installed. HeteroDataBuilder requires it.")

class HeteroDataBuilder:
    def __init__(self, processed_dir):
        self.processed_dir = processed_dir

    def build(self):
        if torch is None:
            raise ImportError("PyTorch and PyTorch Geometric are required.")
            
        print("Loading Processed CSVs...")
        # Load Nodes
        acc_df = pd.read_csv(os.path.join(self.processed_dir, 'nodes_account.csv'))
        dev_df = pd.read_csv(os.path.join(self.processed_dir, 'nodes_device.csv'))
        ip_df = pd.read_csv(os.path.join(self.processed_dir, 'nodes_ip.csv'))

        # Load Edges
        sends_df = pd.read_csv(os.path.join(self.processed_dir, 'edges_sends.csv'))
        uses_df = pd.read_csv(os.path.join(self.processed_dir, 'edges_uses.csv'))
        logs_df = pd.read_csv(os.path.join(self.processed_dir, 'edges_logs_in.csv'))

        print("Mapping IDs to Continuous Integer Indices...")
        acc_mapping = {id: i for i, id in enumerate(acc_df['account_id'])}
        dev_mapping = {id: i for i, id in enumerate(dev_df['device_id'])}
        ip_mapping = {id: i for i, id in enumerate(ip_df['ip_address'])}

        data = HeteroData()

        # Node Features Initialization
        # Account features could be initialized with degrees/volumes from System 2
        data['account'].x = torch.ones((len(acc_df), 3), dtype=torch.float)
        data['device'].x = torch.ones((len(dev_df), 1), dtype=torch.float)
        data['ip'].x = torch.ones((len(ip_df), 1), dtype=torch.float)

        print("Constructing PyG Edge Tensors...")
        # Edge 1: Sends
        # Calculate time delta for edge attribute (temporal feature)
        sends_df['time_delta'] = sends_df.groupby('src')['timestamp'].diff().fillna(0)
        
        src_acc = [acc_mapping[src] for src in sends_df['src']]
        dst_acc = [acc_mapping[dst] for dst in sends_df['dst']]
        data['account', 'sends', 'account'].edge_index = torch.tensor([src_acc, dst_acc], dtype=torch.long)
        data['account', 'sends', 'account'].edge_attr = torch.tensor(sends_df[['amount', 'time_delta']].values, dtype=torch.float)
        data['account', 'sends', 'account'].y = torch.tensor(sends_df['label'].values, dtype=torch.float)

        # Edge 2: Uses Device
        src_uses = [acc_mapping[src] for src in uses_df['src']]
        dst_uses = [dev_mapping[dst] for dst in uses_df['dst']]
        data['account', 'uses', 'device'].edge_index = torch.tensor([src_uses, dst_uses], dtype=torch.long)

        # Edge 3: Logs In From IP
        src_logs = [acc_mapping[src] for src in logs_df['src']]
        dst_logs = [ip_mapping[dst] for dst in logs_df['dst']]
        data['account', 'logs_in', 'ip'].edge_index = torch.tensor([src_logs, dst_logs], dtype=torch.long)

        print("Generating Strict Temporal Split Masks...")
        n_edges = len(sends_df)
        train_end = int(n_edges * 0.7)
        val_end = int(n_edges * 0.85)

        train_mask = torch.zeros(n_edges, dtype=torch.bool)
        val_mask = torch.zeros(n_edges, dtype=torch.bool)
        test_mask = torch.zeros(n_edges, dtype=torch.bool)

        train_mask[:train_end] = True
        val_mask[train_end:val_end] = True
        test_mask[val_end:] = True

        data['account', 'sends', 'account'].train_mask = train_mask
        data['account', 'sends', 'account'].val_mask = val_mask
        data['account', 'sends', 'account'].test_mask = test_mask

        return data

if __name__ == "__main__":
    proc_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')
    if os.path.exists(proc_dir) and torch is not None:
        builder = HeteroDataBuilder(proc_dir)
        hetero_graph = builder.build()
        print("HeteroData Output Shape:")
        print(hetero_graph)
