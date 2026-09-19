# Master ML Implementation Plan

This document outlines the exact end-to-end implementation pipelines for the Machine Learning component.

## Pipeline A: Offline Training Pipeline
**Input:** Historical Financial Dataset (IBM AML) -> **Processing:** GNN Training Loop -> **Output:** Trained Model Artifact (.onnx)

1. **Data Ingestion:** Load raw CSVs using Pandas.
2. **Graph Mapping:** Construct the global heterogeneous graph in memory (NetworkX / PyG).
3. **Temporal Splitting:** Slice the graph temporally (e.g., train on months 1-6, validate on month 7, test on month 8).
4. **Mini-batching:** Use PyG's NeighborLoader to sample k-hop subgraphs for scalable training.
5. **Model Training:** Forward pass through the HGTConv / SAGEConv layers, calculate BCE Loss, backpropagate.
6. **Export:** Freeze the best model weights and export to ONNX.

## Pipeline B: Real-Time Inference Pipeline (<15ms)
**Input:** Single New Transaction Event -> **Processing:** Triton GNN Inference -> **Output:** Fraud Score & Explanation

1. **Event Trigger:** Backend receives transaction, triggers ML API.
2. **Subgraph Extraction:** Query Memgraph for the 2-hop neighborhood surrounding the sender and receiver accounts.
3. **Feature Retrieval:** Fetch historical tabular features for these nodes from Redis.
4. **PyG Construction:** Instantly build the local HeteroData subgraph.
5. **Triton Execution:** Send subgraph to NVIDIA Triton via gRPC. Triton batches it and runs the ONNX model.
6. **XAI Trigger (Async):** If the fraud score exceeds the threshold (e.g., > 0.85), asynchronously run the PyG Explainer to extract contributing edges.
7. **Response:** Return score and explanation to the FastAPI backend for WebSocket broadcasting.
