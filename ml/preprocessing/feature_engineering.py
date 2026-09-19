import pandas as pd
import numpy as np
import pickle
import os
from sklearn.preprocessing import StandardScaler

class FeatureEngineer:
    def __init__(self, edges_filepath, artifacts_dir=None):
        self.edges_filepath = edges_filepath
        self.artifacts_dir = artifacts_dir

    def build_features(self):
        print("Loading edge data...")
        df = pd.read_csv(self.edges_filepath)
        
        print("Downcasting Pandas datatypes to prevent System RAM OOM crashes...")
        for col in df.columns:
            if df[col].dtype == 'float64':
                df[col] = pd.to_numeric(df[col], downcast='float')
            elif df[col].dtype == 'int64':
                df[col] = pd.to_numeric(df[col], downcast='integer')
                
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

        # Calculate transaction velocity / time delta
        df['time_delta'] = df.groupby('src')['timestamp'].diff().fillna(0)
        
        print("Normalizing continuous features to prevent exploding gradients...")
        scaler = StandardScaler()
        
        # Scale amount and time_delta specifically for the neural network
        df[['amount', 'time_delta']] = scaler.fit_transform(df[['amount', 'time_delta']])
        
        if self.artifacts_dir:
            os.makedirs(self.artifacts_dir, exist_ok=True)
            scaler_path = os.path.join(self.artifacts_dir, 'scaler.pkl')
            with open(scaler_path, 'wb') as f:
                pickle.dump(scaler, f)
            print(f"Scaler successfully saved to {scaler_path} for backend inference.")

        print("Feature engineering complete.")
        features = ['amount', 'hour_of_day', 's_out_degree', 's_total_sent', 'r_in_degree', 'r_total_received', 'time_delta']
        
        return df, features
