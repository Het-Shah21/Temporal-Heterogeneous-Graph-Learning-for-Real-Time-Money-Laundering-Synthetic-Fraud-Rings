# ML Decision Log

*This document tracks all decisions made during the development of the ML portion.*

### Decision 001: Dataset Selection Strategy
- **What:** Decided to pivot from a purely custom naive simulator to adopting structures and data from the IBM AML (Anti-Money Laundering) Dataset.
- **Why:** Purely synthetic data fails to capture the realistic noise and hidden topological structures (cycles, layering, smurfing) present in actual financial crimes. The IBM AML dataset uses a multi-agent simulation that closely mimics real-world banking logic.
- **Where:** ml/data/ module.
- **When:** Week 1, Phase 1 (Project Initiation).

### Decision 002: Deterministic Heterogeneous Augmentation
- **What:** Decided to computationally augment the homogeneous IBM AML dataset using deterministic SHA-256 hashing based on Account_ID to generate static Device_IDs and IP_Addresses. Overwritten for fraud rings to share identical hardware.
- **Why:** Real banking logs hide IPs/Devices for privacy. Pure synthetic data lacks structure. This hybrid approach guarantees we have a strictly heterogeneous graph schema without losing the realistic transactional flow of the IBM dataset.
- **Where:** ml/data/hetero_builder.py
- **When:** Week 1, Phase 1 (Data Acquisition).

### Decision 003: Strict Temporal Splitting for Model Evaluation
- **What:** Decided to use strict chronological slicing (first 70% of transactions for training, next 15% for validation, final 15% for testing) sorted by timestamp, explicitly bypassing standard random sampling.
- **Why:** In financial datasets, random splitting causes future-data leakage (the model learns from future fraud behaviors to predict past behaviors). A strict temporal split perfectly mirrors the real-world production scenario.
- **Where:** ml/models/baseline.py (and will apply to the upcoming GNN).
- **When:** Week 2, Phase 3 (Baseline Modeling).

### Decision 004: Edge Classification Formulation

- **What:** Decided to formulate fraud detection as an Edge Classification problem rather than a Node Classification problem.
- **Why:** Fraud is an event (a transaction) occurring between two accounts at a specific time. If we classify nodes, we permanently label an account as "fraudulent", missing the temporal nuance that legitimate accounts can be momentarily hijacked (mule accounts). Classifying the edge accurately pinpoints the exact illicit event.
- **Where:** `ml/models/gnn.py`
- **When:** Week 2, Phase 4 (GNN Architecture).

### Decision 005: Triton ONNX over TorchServe

- **What:** Decided to export the model exclusively to ONNX format using Dynamic Axes for serving on NVIDIA Triton Inference Server, rather than deploying natively with FastAPI + PyTorch or TorchServe.
- **Why:** The strict <15ms latency target cannot be met by standard Python-GIL bound PyTorch inference under heavy load. Triton provides native C++ TensorRT optimization and dynamic batching.
- **Where:** `ml/export/triton_exporter.py`
- **When:** Week 3, Phase 5 (XAI & Deployment Prep).
