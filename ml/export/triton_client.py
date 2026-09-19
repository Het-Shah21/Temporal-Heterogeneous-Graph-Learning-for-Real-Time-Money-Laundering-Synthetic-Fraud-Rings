import numpy as np
import pickle
import os

try:
    import tritonclient.http as httpclient
except ImportError:
    httpclient = None

class TritonFraudClient:
    def __init__(self, url="localhost:8000", model_name="gnn_fraud", artifacts_dir=None):
        self.url = url
        self.model_name = model_name
        self.artifacts_dir = artifacts_dir
        self.edge_scaler = self._load_scaler('scaler.pkl')
        self.node_scaler = self._load_scaler('node_scaler.pkl')
        
        if httpclient is not None:
            self.client = httpclient.InferenceServerClient(url=self.url)
        else:
            self.client = None

    def _load_scaler(self, filename):
        if not self.artifacts_dir:
            return None
        scaler_path = os.path.join(self.artifacts_dir, filename)
        if os.path.exists(scaler_path):
            with open(scaler_path, 'rb') as f:
                return pickle.load(f)
        return None

    def predict_fraud(self, sender_idx, receiver_idx, raw_amount, raw_time_delta, 
                      subgraph_x, subgraph_edge_index, subgraph_edge_attr):
        """
        Bridge for FastAPI Backend to call Triton.
        """
        # 1. Scale continuous edge features
        if self.edge_scaler:
            scaled_feats = self.edge_scaler.transform([[raw_amount, raw_time_delta]])
            amount, time_delta = scaled_feats[0][0], scaled_feats[0][1]
        else:
            amount, time_delta = raw_amount, raw_time_delta

        # 1b. Scale continuous node features (Fetched from Redis raw)
        if self.node_scaler:
            subgraph_x = self.node_scaler.transform(subgraph_x)

        # 2. Format as PyTorch/ONNX expected FP32/INT64 numpy arrays
        x_arr = np.array(subgraph_x, dtype=np.float32)
        
        edge_index_arr = np.array(subgraph_edge_index, dtype=np.int64)
        if len(edge_index_arr.shape) == 1:
            edge_index_arr = edge_index_arr.reshape(2, 0)
            
        edge_attr_arr = np.array(subgraph_edge_attr, dtype=np.float32)
        if len(edge_attr_arr.shape) == 1:
            edge_attr_arr = edge_attr_arr.reshape(0, 2)

        # 3. CRITICAL LOGIC: Inject pending transaction edge
        new_edge = np.array([[sender_idx], [receiver_idx]], dtype=np.int64)
        edge_index_arr = np.hstack((edge_index_arr, new_edge))
        
        new_attr = np.array([[amount, time_delta]], dtype=np.float32)
        edge_attr_arr = np.vstack((edge_attr_arr, new_attr))
        
        target_edge_idx = edge_index_arr.shape[1] - 1

        # 4. Network Call to Triton Server
        if self.client is None:
            return {"fraud_probability": 0.0, "status": "mock_success", "target_edge_idx": target_edge_idx}

        inputs = [
            httpclient.InferInput("x_account", x_arr.shape, "FP32"),
            httpclient.InferInput("edge_index_sends", edge_index_arr.shape, "INT64"),
            httpclient.InferInput("edge_attr_sends", edge_attr_arr.shape, "FP32")
        ]
        inputs[0].set_data_from_numpy(x_arr)
        inputs[1].set_data_from_numpy(edge_index_arr)
        inputs[2].set_data_from_numpy(edge_attr_arr)

        response = self.client.infer(self.model_name, inputs)
        fraud_probs = response.as_numpy("fraud_prob")
        fraud_prob = fraud_probs[target_edge_idx]
        
        return {"fraud_probability": float(fraud_prob), "status": "success"}
