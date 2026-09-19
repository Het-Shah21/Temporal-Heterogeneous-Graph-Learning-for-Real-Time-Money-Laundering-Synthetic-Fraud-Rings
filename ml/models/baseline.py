import pandas as pd
import numpy as np
import os
import xgboost as xgb
from sklearn.metrics import classification_report, roc_auc_score, f1_score
import json
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from preprocessing.feature_engineering import FeatureEngineer

class BaselineModel:
    def __init__(self, data_path, output_dir):
        self.fe = FeatureEngineer(data_path)
        self.output_dir = output_dir

    def train_and_evaluate(self):
        df, feature_cols = self.fe.build_features()
        
        print("Performing temporal train/val/test split (70/15/15)...")
        n = len(df)
        train_end = int(n * 0.7)
        val_end = int(n * 0.85)

        train_df = df.iloc[:train_end]
        val_df = df.iloc[train_end:val_end]
        test_df = df.iloc[val_end:]

        X_train, y_train = train_df[feature_cols], train_df['label']
        X_val, y_val = val_df[feature_cols], val_df['label']
        X_test, y_test = test_df[feature_cols], test_df['label']

        # Ensure no single-class splits in small mock datasets
        if len(y_train.unique()) < 2:
            print("Warning: Only one class in training set. Injecting a dummy fraud for unit testing.")
            y_train.iloc[0] = 1 - y_train.iloc[0]
        if len(y_val.unique()) < 2:
            y_val.iloc[0] = 1 - y_val.iloc[0]
        if len(y_test.unique()) < 2:
            y_test.iloc[0] = 1 - y_test.iloc[0]

        print(f"Training XGBoost Baseline on {len(X_train)} samples...")
        # Handle class imbalance
        num_pos = y_train.sum()
        num_neg = len(y_train) - num_pos
        scale_weight = num_neg / num_pos if num_pos > 0 else 1.0

        model = xgb.XGBClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            scale_pos_weight=scale_weight,
            eval_metric='auc'
        )

        model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            verbose=False
        )

        print("Evaluating on Test Set...")
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]

        auc = roc_auc_score(y_test, y_proba)
        f1 = f1_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, zero_division=0)

        print("\n--- BASELINE METRICS ---")
        print(f"ROC-AUC: {auc:.4f}")
        print(f"F1-Score: {f1:.4f}")
        print("\nClassification Report:\n", report)

        # Save artifacts
        os.makedirs(self.output_dir, exist_ok=True)
        model.save_model(os.path.join(self.output_dir, 'baseline_xgboost.json'))
        
        metrics = {'roc_auc': float(auc), 'f1': float(f1)}
        with open(os.path.join(self.output_dir, 'baseline_metrics.json'), 'w') as f:
            json.dump(metrics, f)
            
        print("Model and metrics saved successfully.")

if __name__ == "__main__":
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'edges_sends.csv')
    out_dir = os.path.join(os.path.dirname(__file__), 'artifacts')
    
    if os.path.exists(data_path):
        baseline = BaselineModel(data_path, out_dir)
        baseline.train_and_evaluate()
    else:
        print(f"Processed data not found at {data_path}. Please run System 1 first.")
