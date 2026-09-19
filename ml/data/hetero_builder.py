import pandas as pd
import hashlib
import os

class HeteroGraphBuilder:
    def __init__(self, raw_filepath, output_dir):
        self.raw_filepath = raw_filepath
        self.output_dir = output_dir

    def _hash_to_id(self, input_string, prefix):
        # Deterministic hash to generate realistic IDs
        hash_obj = hashlib.sha256(input_string.encode('utf-8')).hexdigest()
        return f"{prefix}_{hash_obj[:12]}"

    def process(self):
        print(f"Loading data from {self.raw_filepath}...")
        df = pd.read_csv(self.raw_filepath)

        # 1. Sort temporally
        if 'Timestamp' in df.columns:
            df = df.sort_values(by='Timestamp').reset_index(drop=True)

        print("Extracting nodes...")
        # 2. Extract unique accounts
        accounts = pd.concat([df['From_Account'], df['To_Account']]).unique()
        df_accounts = pd.DataFrame({'account_id': accounts})

        # 3. Augment Heterogeneous Nodes (Devices & IPs)
        # We simulate devices/IPs. If Is_Laundering=1, sender and receiver share the same device/IP.
        print("Augmenting Device and IP data...")
        
        device_map = {}
        ip_map = {}
        
        # Default assignment
        for acc in accounts:
            device_map[acc] = self._hash_to_id(str(acc) + "_device", "DEV")
            ip_map[acc] = self._hash_to_id(str(acc) + "_ip", "IP")
            
        # Fraud Ring Overwrite: Force shared infrastructure for illicit transactions
        if 'Is_Laundering' in df.columns:
            fraud_txns = df[df['Is_Laundering'] == 1]
            for _, row in fraud_txns.iterrows():
                sender = row['From_Account']
                receiver = row['To_Account']
                # Both use the sender's device and IP to simulate a coordinated mule ring
                device_map[receiver] = device_map[sender]
                ip_map[receiver] = ip_map[sender]

        # Extract unique devices and IPs
        unique_devices = list(set(device_map.values()))
        unique_ips = list(set(ip_map.values()))
        
        df_devices = pd.DataFrame({'device_id': unique_devices})
        df_ips = pd.DataFrame({'ip_address': unique_ips})

        print("Constructing edges...")
        # 4. Construct Edges
        # Edge 1: Account -> SENDS -> Account
        df_sends = df[['From_Account', 'To_Account', 'Amount_Received', 'Timestamp', 'Is_Laundering']].copy()
        df_sends.rename(columns={'From_Account': 'src', 'To_Account': 'dst', 'Amount_Received': 'amount', 'Timestamp': 'timestamp', 'Is_Laundering': 'label'}, inplace=True)

        # Edge 2 & 3: Account -> USES -> Device, Account -> LOGS_IN_FROM -> IP
        uses_edges = [{'src': acc, 'dst': dev} for acc, dev in device_map.items()]
        logs_edges = [{'src': acc, 'dst': ip} for acc, ip in ip_map.items()]
        
        df_uses = pd.DataFrame(uses_edges)
        df_logs = pd.DataFrame(logs_edges)

        print("Exporting to processed directory...")
        # 5. Export
        os.makedirs(self.output_dir, exist_ok=True)
        df_accounts.to_csv(os.path.join(self.output_dir, 'nodes_account.csv'), index=False)
        df_devices.to_csv(os.path.join(self.output_dir, 'nodes_device.csv'), index=False)
        df_ips.to_csv(os.path.join(self.output_dir, 'nodes_ip.csv'), index=False)
        df_sends.to_csv(os.path.join(self.output_dir, 'edges_sends.csv'), index=False)
        df_uses.to_csv(os.path.join(self.output_dir, 'edges_uses.csv'), index=False)
        df_logs.to_csv(os.path.join(self.output_dir, 'edges_logs_in.csv'), index=False)
        
        print("Heterogeneous Graph Construction Complete.")

if __name__ == "__main__":
    # Intended to be run when actual CSV is placed in raw/
    raw_path = os.path.join(os.path.dirname(__file__), 'raw', 'ibm_transactions.csv')
    out_path = os.path.join(os.path.dirname(__file__), 'processed')
    if os.path.exists(raw_path):
        builder = HeteroGraphBuilder(raw_path, out_path)
        builder.process()
    else:
        print(f"Waiting for raw data at {raw_path}")
