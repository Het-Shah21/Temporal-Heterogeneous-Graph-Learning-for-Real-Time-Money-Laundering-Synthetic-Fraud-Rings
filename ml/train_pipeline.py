import os
import sys

# Add current dir to path for internal imports
sys.path.append(os.path.dirname(__file__))

try:
    import torch
    from preprocessing.graph_builder import HeteroDataBuilder
    from models.gnn import HeteroFraudGNN, train_epoch, evaluate_model, get_criterion
    from export.triton_exporter import TritonExporter
    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False

def run_pipeline():
    print("=== STARTING ML TRAINING PIPELINE ===")
    
    if not HAS_DEPS:
        print("ERROR: PyTorch or PyTorch Geometric is not installed.")
        print("Please install dependencies to run the full pipeline.")
        return

    # 1. Setup Directories
    base_dir = os.path.dirname(__file__)
    proc_dir = os.path.join(base_dir, 'data', 'processed')
    artifacts_dir = os.path.join(base_dir, 'models', 'artifacts')
    os.makedirs(artifacts_dir, exist_ok=True)
    
    if not os.path.exists(proc_dir) or not os.listdir(proc_dir):
        print("ERROR: Processed data not found. Please run System 1 (data processing) first.")
        print(f"Looking for data in: {proc_dir}")
        return

    # 2. Build Graph
    print("\n[1/4] Building Heterogeneous Graph...")
    try:
        builder = HeteroDataBuilder(proc_dir)
        data = builder.build()
    except Exception as e:
        print(f"Failed to build graph. Please ensure the CSV format is correct. Error: {e}")
        return

    # 3. Initialize Model
    print("\n[2/4] Initializing PyTorch GNN...")
    hidden_channels = 64
    out_channels = 1
    model = HeteroFraudGNN(hidden_channels=hidden_channels, out_channels=out_channels)
    
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.005, weight_decay=1e-4)
    criterion = get_criterion(data)

    # 4. Training Loop
    print("\n[3/4] Training Model (100 Epochs)...")
    best_val_auc = 0.0
    epochs = 100
    
    for epoch in range(1, epochs + 1):
        loss = train_epoch(model, optimizer, data, criterion)
        
        if epoch % 20 == 0:
            print(f"Epoch {epoch:03d} | Loss: {loss:.4f}")
            val_auc, val_f1 = evaluate_model(model, data, mask_name='val_mask')
            
            # Model Checkpointing (Saving the Weights)
            if val_auc >= best_val_auc:
                best_val_auc = val_auc
                pth_path = os.path.join(artifacts_dir, 'gnn_model.pth')
                torch.save(model.state_dict(), pth_path)
                print(f" -> Checkpoint saved (AUC: {val_auc:.4f}) to {pth_path}")

    print("\n=== FINAL TEST EVALUATION ===")
    # Load best model for testing
    best_model_path = os.path.join(artifacts_dir, 'gnn_model.pth')
    if os.path.exists(best_model_path):
        model.load_state_dict(torch.load(best_model_path))
    evaluate_model(model, data, mask_name='test_mask')

    # 5. Export to Triton
    print("\n[4/4] Exporting to NVIDIA Triton (ONNX)...")
    export_dir = os.path.join(base_dir, 'export', 'triton_model_repository', 'gnn_fraud', '1')
    exporter = TritonExporter(model, export_dir)
    exporter.export_to_onnx()
    exporter.generate_config()
    
    print("\n=== PIPELINE COMPLETE ===")

if __name__ == "__main__":
    run_pipeline()
