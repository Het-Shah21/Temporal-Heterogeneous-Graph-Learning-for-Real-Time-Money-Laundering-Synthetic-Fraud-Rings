import os
try:
    import torch
    import torch.nn as nn
except ImportError:
    torch = None
    nn = None

class GNNONNXWrapper(nn.Module):
    """
    ONNX does not support Python dictionaries. 
    This wrapper translates flat C++ arrays from Triton into PyG nested dictionaries.
    """
    def __init__(self, model):
        super().__init__()
        self.model = model

    def forward(self, x_account, edge_index_sends, edge_attr_sends):
        # Dynamically reconstruct the PyG Dictionary structure expected by the model
        device = x_account.device
        x_dict = {
            'account': x_account,
            # Provide dummy tensors for unused heterogeneous nodes to satisfy PyG convolutions
            'device': torch.zeros((1, 1), device=device, dtype=torch.float32),
            'ip': torch.zeros((1, 1), device=device, dtype=torch.float32)
        }
        edge_index_dict = {
            ('account', 'sends', 'account'): edge_index_sends,
            ('account', 'uses', 'device'): torch.empty((2, 0), device=device, dtype=torch.long),
            ('account', 'logs_in', 'ip'): torch.empty((2, 0), device=device, dtype=torch.long)
        }
        edge_attr_dict = {
            ('account', 'sends', 'account'): edge_attr_sends
        }
        logits = self.model(x_dict, edge_index_dict, edge_attr_dict)
        # HARDWARE LOGIC: Compress raw training logits into a true percentage (0.0 to 1.0)
        return torch.sigmoid(logits)

class TritonExporter:
    def __init__(self, model, output_dir):
        self.model = model
        self.output_dir = output_dir

    def export_to_onnx(self):
        if torch is None:
            print("PyTorch not installed. Cannot export ONNX.")
            return
            
        os.makedirs(self.output_dir, exist_ok=True)
        onnx_path = os.path.join(self.output_dir, "model.onnx")
        
        wrapper = GNNONNXWrapper(self.model)
        wrapper.eval()

        # Dummy inputs for tracing the ONNX computational graph
        x_account = torch.randn(5, 4, dtype=torch.float32)
        edge_index_sends = torch.randint(0, 5, (2, 4), dtype=torch.long)
        edge_attr_sends = torch.randn(4, 2, dtype=torch.float32)

        try:
            torch.onnx.export(
                wrapper,
                (x_account, edge_index_sends, edge_attr_sends),
                onnx_path,
                export_params=True,
                opset_version=14,
                do_constant_folding=True,
                input_names=['x_account', 'edge_index_sends', 'edge_attr_sends'],
                output_names=['fraud_prob'],
                dynamic_axes={
                    'x_account': {0: 'num_nodes'},
                    'edge_index_sends': {1: 'num_edges'},
                    'edge_attr_sends': {0: 'num_edges'},
                    'fraud_prob': {0: 'num_edges'}
                }
            )
            print(f"Exported TRUE ONNX compiled binary to {onnx_path}")
        except Exception as e:
            print(f"ONNX Export Compilation Failed: {e}")

    def generate_config(self):
        config = """name: "gnn_fraud"
platform: "onnxruntime_onnx"
max_batch_size: 128
input [
  {
    name: "x_account"
    data_type: TYPE_FP32
    dims: [ -1, 4 ]
  },
  {
    name: "edge_index_sends"
    data_type: TYPE_INT64
    dims: [ 2, -1 ]
  },
  {
    name: "edge_attr_sends"
    data_type: TYPE_FP32
    dims: [ -1, 2 ]
  }
]
output [
  {
    name: "fraud_prob"
    data_type: TYPE_FP32
    dims: [ -1 ]
  }
]
"""
        config_path = os.path.join(os.path.dirname(self.output_dir), "config.pbtxt")
        with open(config_path, 'w') as f:
            f.write(config)
        print(f"Triton config dynamically generated at {config_path}")
