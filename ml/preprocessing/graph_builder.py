import os
import pandas as pd
import numpy as np
import pickle

try:
    import torch
    from torch_geometric.data import HeteroData
    from preprocessing.feature_engineering import FeatureEngineer
except ImportError:
    torch = None
    HeteroData = None

class HeteroDataBuilder:
    def __init__(self, processed_dir):
        self.processed_dir = processed_dir
        self.artifacts_dir = os.path.join(self.processed_dir, '..', '..', 'models', 'artifacts')

    def safe_map_edges(self, df, src_col, dst_col, src_map, dst_map):
        """Defensively maps edges, ignoring orphaned data that would cause KeyErrors."""
        valid_src, valid_dst, valid_indices = [], [], []
        for idx, (s, d) in enumerate(zip(df[src_col], df[dst_col])):
            if s in src_map and d in dst_map:
                valid_src.append(src_map[s])
                valid_dst.append(dst_map[d])
                valid_indices.append(idx)
        
        dropped = len(df) - len(valid_indices)
        if dropped > 0:
            print(f"WARNING: Dropped {dropped} orphaned edges due to missing nodes in {src_col}/{dst_col}")
            
        return valid_src, valid_dst, valid_indices

    def build(self):
        if torch is None:
            raise ImportError("PyTorch and PyTorch Geometric are required.")
            
        print("Loading Nodes...")
        acc_df = pd.read_csv(os.path.join(self.processed_dir, 'nodes_account.csv'))
        dev_df = pd.read_csv(os.path.join(self.processed_dir, 'nodes_device.csv'))
        ip_df = pd.read_csv(os.path.join(self.processed_dir, 'nodes_ip.csv'))

        print("Applying Unified Feature Engineering (Edge Scaler)...")
        fe = FeatureEngineer(os.path.join(self.processed_dir, 'edges_sends.csv'), self.artifacts_dir)
        sends_df, _ = fe.build_features() # Amount and time_delta are now mathematically scaled
        
        uses_df = pd.read_csv(os.path.join(self.processed_dir, 'edges_uses.csv'))
        logs_df = pd.read_csv(os.path.join(self.processed_dir, 'edges_logs_in.csv'))

        acc_mapping = {id: i for i, id in enumerate(acc_df['account_id'])}
        dev_mapping = {id: i for i, id in enumerate(dev_df['device_id'])}
        ip_mapping = {id: i for i, id in enumerate(ip_df['ip_address'])}

        data = HeteroData()

        print("Aggregating historical node features for Redis and PyG...")
        s_grouped = sends_df.groupby('src').agg(
            out_degree=('amount', 'count'),
            total_sent=('amount', 'sum')
        ).to_dict('index')
        r_grouped = sends_df.groupby('dst').agg(
            in_degree=('amount', 'count'),
            total_received=('amount', 'sum')
        ).to_dict('index')

        acc_features_raw = {}
        acc_tensor = np.zeros((len(acc_mapping), 4))
        
        for acc_id, i in acc_mapping.items():
            out_deg = s_grouped.get(acc_id, {}).get('out_degree', 0.0)
            t_sent = s_grouped.get(acc_id, {}).get('total_sent', 0.0)
            in_deg = r_grouped.get(acc_id, {}).get('in_degree', 0.0)
            t_recv = r_grouped.get(acc_id, {}).get('total_received', 0.0)
            
            # HARDWARE LOGIC: Strict positional array to prevent JSON key-order scrambling on the backend
            acc_features_raw[str(acc_id)] = [
                float(out_deg), float(t_sent), float(in_deg), float(t_recv)
            ]
            acc_tensor[i] = [out_deg, t_sent, in_deg, t_recv]

        import json
        os.makedirs(self.artifacts_dir, exist_ok=True)
        with open(os.path.join(self.artifacts_dir, 'redis_node_features.json'), 'w') as f:
            json.dump(acc_features_raw, f)

        from sklearn.preprocessing import StandardScaler
        node_scaler = StandardScaler()
        acc_tensor_scaled = node_scaler.fit_transform(acc_tensor)
        
        with open(os.path.join(self.artifacts_dir, 'node_scaler.pkl'), 'wb') as f:
            pickle.dump(node_scaler, f)

        data['account'].x = torch.tensor(acc_tensor_scaled, dtype=torch.float)
        data['device'].x = torch.ones((len(dev_df), 1), dtype=torch.float)
        data['ip'].x = torch.ones((len(ip_df), 1), dtype=torch.float)

        print("Constructing PyG Edge Tensors (Defensive Mapping)...")
        # Defensive Mapping applied to prevent KeyError crashes
        src_acc, dst_acc, valid_sends = self.safe_map_edges(sends_df, 'src', 'dst', acc_mapping, acc_mapping)
        sends_df = sends_df.iloc[valid_sends].reset_index(drop=True)
        
        data['account', 'sends', 'account'].edge_index = torch.tensor([src_acc, dst_acc], dtype=torch.long)
        data['account', 'sends', 'account'].edge_attr = torch.tensor(sends_df[['amount', 'time_delta']].values, dtype=torch.float)
        data['account', 'sends', 'account'].y = torch.tensor(sends_df['label'].values, dtype=torch.float)

        src_uses, dst_uses, _ = self.safe_map_edges(uses_df, 'src', 'dst', acc_mapping, dev_mapping)
        data['account', 'uses', 'device'].edge_index = torch.tensor([src_uses, dst_uses], dtype=torch.long)

        src_logs, dst_logs, _ = self.safe_map_edges(logs_df, 'src', 'dst', acc_mapping, ip_mapping)
        data['account', 'logs_in', 'ip'].edge_index = torch.tensor([src_logs, dst_logs], dtype=torch.long)

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
