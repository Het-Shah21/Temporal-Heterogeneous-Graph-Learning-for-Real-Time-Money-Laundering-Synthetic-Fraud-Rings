# ML Implementation Phases & Tasks

## Phase 1: Data Acquisition & Preprocessing
- [ ] Research and download IBM AML Dataset (or equivalent PaySim).
- [x] Write data parsers to convert dataset CSVs into our standard Node/Edge schema.
- [ ] Build tabular feature extractors (velocity, volume, degree).

## Phase 2: Graph Construction
- [ ] Implement PyG Dataset or HeteroData constructor.
- [ ] Validate heterogeneous schema (User, Account, Device, IP).
- [ ] Create train/val/test splits based on temporal ordering (Time-based split).

## Phase 3: Baseline Modeling
- [x] Train XGBoost model on tabular features.
- [x] Generate classification report and ROC-AUC curve.
- [x] Document baseline results.

## Phase 4: GNN Architecture Development
- [x] Implement HeteroConv neural network in PyTorch.
- [x] Write the training loop (optimizer, loss function, evaluation step).
- [x] Tune hyperparameters (learning rate, hidden dimensions).
- [x] Compare GNN performance against XGBoost.

## Phase 5: XAI & Triton Export
- [x] Integrate PyG Explainer.
- [x] Generate human-readable explanation masks for the dashboard.
- [x] Convert the final GNN model to ONNX format.
- [x] Configure Triton Inference Server model repository.
