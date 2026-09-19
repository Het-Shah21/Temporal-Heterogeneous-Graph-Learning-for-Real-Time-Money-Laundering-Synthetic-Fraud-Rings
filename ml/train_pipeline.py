import os
import sys
import json
import logging
import random
import numpy as np

sys.path.append(os.path.dirname(__file__))

try:
    import torch
    from torch_geometric.loader import NeighborLoader
    from preprocessing.graph_builder import HeteroDataBuilder
    from models.gnn import HeteroFraudGNN, train_epoch, evaluate_model, get_criterion
    from export.triton_exporter import TritonExporter
    from models.baseline import BaselineModel
    from xai.explainer import FraudExplainer
    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False

def set_global_seeds(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    if HAS_DEPS and torch is not None:
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed(seed)
            torch.cuda.manual_seed_all(seed)
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False

def setup_logger(artifacts_dir):
    logger = logging.getLogger('ML_Pipeline')
    logger.setLevel(logging.INFO)
    if logger.hasHandlers():
        logger.handlers.clear()
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    
    fh = logging.FileHandler(os.path.join(artifacts_dir, 'training_run.log'))
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger

def run_pipeline():
    base_dir = os.path.dirname(__file__)
    proc_dir = os.path.join(base_dir, 'data', 'processed')
    artifacts_dir = os.path.join(base_dir, 'models', 'artifacts')
    os.makedirs(artifacts_dir, exist_ok=True)
    
    logger = setup_logger(artifacts_dir)
    logger.info("=== STARTING ML TRAINING PIPELINE ===")
    
    set_global_seeds(42)
    logger.info("Global RNG seeds locked to 42 for strict scientific reproducibility.")
    
    if not HAS_DEPS:
        logger.error("Dependencies not installed. Please run `pip install -r requirements.txt`")
        return

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    logger.info(f"[Hardware] Compute Device Selected: {device}")

    logger.info("[1/6] Training XGBoost Baseline Model...")
    data_path = os.path.join(proc_dir, 'edges_sends.csv')
    try:
        baseline = BaselineModel(data_path, artifacts_dir)
        baseline.train_and_evaluate()
    except Exception as e:
        logger.warning(f"Baseline training failed: {e}")

    logger.info("[2/6] Building Heterogeneous Graph & Node Features...")
    try:
        builder = HeteroDataBuilder(proc_dir)
        data = builder.build()
        # HARDWARE LOGIC: Keep the massive 4GB graph natively on the CPU! Do not use .to(device)
    except Exception as e:
        logger.error(f"Failed to build graph: {e}")
        return

    logger.info("[3/6] Initializing Minibatch NeighborLoader & PyTorch GNN...")
    # HARDWARE LOGIC: Minibatching limits GPU memory to <2GB perfectly via Subgraph Streaming
    train_loader = NeighborLoader(
        data,
        num_neighbors=[15, 10], # 2-hop subgraphs
        input_nodes=('account', torch.ones(data['account'].num_nodes, dtype=torch.bool)),
        batch_size=4096,
        shuffle=True
    )

    hidden_channels = 64
    out_channels = 1
    model = HeteroFraudGNN(hidden_channels=hidden_channels, out_channels=out_channels).to(device)
    
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.005, weight_decay=1e-4)
    criterion = get_criterion(data).to(device)

    logger.info("[4/6] Training GNN Model (100 Epochs)...")
    best_val_auc = 0.0
    epochs = 100
    
    for epoch in range(1, epochs + 1):
        loss = train_epoch(model, optimizer, train_loader, criterion, device)
        
        if epoch % 20 == 0:
            logger.info(f"Epoch {epoch:03d} | Minibatch Loss: {loss:.4f}")
            val_auc, val_f1 = evaluate_model(model, train_loader, mask_name='val_mask', device=device)
            
            if val_auc >= best_val_auc:
                best_val_auc = val_auc
                pth_path = os.path.join(artifacts_dir, 'gnn_model.pth')
                torch.save(model.cpu().state_dict(), pth_path)
                model.to(device)
                logger.info(f" -> CPU-Safe Checkpoint saved (AUC: {val_auc:.4f}) to {pth_path}")

    logger.info("=== FINAL TEST EVALUATION (GNN) ===")
    best_model_path = os.path.join(artifacts_dir, 'gnn_model.pth')
    if os.path.exists(best_model_path):
        model.load_state_dict(torch.load(best_model_path, map_location=torch.device('cpu')))
        model.to(device)
    evaluate_model(model, train_loader, mask_name='test_mask', device=device)

    logger.info("[5/6] Verifying Explainable AI (XAI) System...")
    try:
        model.eval()
        explainer = FraudExplainer(model)
        test_edges = data['account', 'sends', 'account'].test_mask.nonzero(as_tuple=True)[0]
        if len(test_edges) > 0:
            sample_edge_idx = int(test_edges[0].item())
            x_dict_dev = {k: v.to(device) for k, v in data.x_dict.items()}
            e_idx_dev = {k: v.to(device) for k, v in data.edge_index_dict.items()}
            e_attr_dev = {k: v.to(device) for k, v in data.edge_attr_dict.items()}
            xai_result = explainer.explain_transaction(
                x_dict_dev, e_idx_dev, e_attr_dev, sample_edge_idx
            )
            xai_out = os.path.join(artifacts_dir, 'xai_sample.json')
            with open(xai_out, 'w') as f:
                json.dump(xai_result, f, indent=4)
            logger.info(f"XAI artifact generated successfully at {xai_out}")
    except Exception as e:
        logger.warning(f"XAI Explainer execution failed: {e}")

    logger.info("[6/6] Exporting GNN to NVIDIA Triton (ONNX)...")
    model.cpu() # Export securely on CPU
    export_dir = os.path.join(base_dir, 'export', 'triton_model_repository', 'gnn_fraud', '1')
    exporter = TritonExporter(model, export_dir)
    exporter.export_to_onnx()
    exporter.generate_config()
    
    logger.info("=== PIPELINE COMPLETE ===")

if __name__ == "__main__":
    run_pipeline()
