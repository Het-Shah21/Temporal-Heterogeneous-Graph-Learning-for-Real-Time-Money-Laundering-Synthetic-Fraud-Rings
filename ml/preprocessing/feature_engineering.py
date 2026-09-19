import pandas as pd
import numpy as np

class FeatureEngineer:
    def __init__(self, edges_filepath):
        self.edges_filepath = edges_filepath

    def build_features(self):
        print("Loading edge data...")
        df = pd.read_csv(self.edges_filepath)
        df = df.sort_values('timestamp').reset_index(drop=True)

        print("Engineering rolling tabular features...")
        
        # Calculate cumulative sender stats
        df['s_out_degree'] = df.groupby('src').cumcount()
        df['s_total_sent'] = df.groupby('src')['amount'].cumsum() - df['amount']

        # Calculate cumulative receiver stats
        df['r_in_degree'] = df.groupby('dst').cumcount()
        df['r_total_received'] = df.groupby('dst')['amount'].cumsum() - df['amount']

        # Hour of day (simulated using modulo 24 if timestamp is an integer sequence)
        df['hour_of_day'] = (df['timestamp'] // 3600) % 24

        print("Feature engineering complete.")
        features = ['amount', 'hour_of_day', 's_out_degree', 's_total_sent', 'r_in_degree', 'r_total_received']
        
        return df, features
