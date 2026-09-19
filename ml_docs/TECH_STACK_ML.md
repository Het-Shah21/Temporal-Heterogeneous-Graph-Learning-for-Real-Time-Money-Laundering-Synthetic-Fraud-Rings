# ML Technology Stack

## 1. Data Processing & Features
- **Pandas / Polars:** For high-speed tabular data manipulation.
- **NetworkX:** For initial graph motif analysis and feature extraction (degree, centrality).

## 2. Machine Learning (Baseline)
- **XGBoost / Scikit-Learn:** For training baseline tabular models (Random Forest, Gradient Boosted Trees).

## 3. Deep Graph Learning (Core)
- **PyTorch (v2.x):** Deep learning backend.
- **PyTorch Geometric (PyG):** Specifically for HeteroData, HeteroConv, SAGEConv, and GATConv layers.

## 4. Explainability (XAI)
- **PyG Explainer / Captum:** For extracting node/edge importance (Shapley Value approximations) to provide auditable compliance flags.

## 5. Deployment & Inference
- **ONNX Runtime:** Exporting PyTorch models to an optimized graph representation.
- **NVIDIA Triton Inference Server:** For sub-15ms inference latency, dynamic batching, and model orchestration via gRPC.
