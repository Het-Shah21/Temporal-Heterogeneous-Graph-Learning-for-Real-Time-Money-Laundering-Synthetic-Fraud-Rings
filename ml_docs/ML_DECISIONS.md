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

### Decision 006: Localized K-Hop Subgraph Inference

- **What:** Decided to extract tiny, localized k-hop subgraphs around the sender/receiver for real-time inference, rather than feeding the global graph.
- **Why:** To satisfy the strict <15ms latency constraint and prevent memory overflow in NVIDIA Triton and the Captum Explainer.
- **Where:** ml/preprocessing/subgraph_extractor.py
- **When:** Week 3, Post-Pipeline Audit.

### Decision 007: GNN Class Imbalance Optimization

- **What:** Decided to dynamically apply `pos_weight` to the `BCEWithLogitsLoss` criterion inside the PyTorch GNN.
- **Why:** Fraud constitutes <1% of the total edges. Without a proportional mathematical penalty for missing a fraudulent transaction, the GNN will suffer from the Accuracy Paradox (predicting 0 for everything and appearing 99% accurate while being completely useless for fraud detection).
- **Where:** `ml/models/gnn.py`
- **When:** Week 3, Post-Pipeline Audit 2.

### Decision 008: Automated ML Pipeline Orchestration

- **What:** Decided to write a monolithic `train_pipeline.py` script that orchestrates the entire ML lifecycle from raw data to Triton ONNX export in a single command.
- **Why:** To eliminate manual operational errors, enable future CI/CD pipeline automation (e.g., Jenkins/GitHub Actions), and guarantee the backend team always receives a synchronized `gnn_model.pth` and `model.onnx`.
- **Where:** `ml/train_pipeline.py`
- **When:** Week 3, Post-Pipeline Audit 3.

### Decision 009: Decoupled Triton Inference Client

- **What:** Decided to author a decoupled inference wrapper (`triton_client.py`) that strictly manages stateful transformations (loading the `StandardScaler` from pickle and formatting PyTorch-compatible NumPy arrays) independently of the FastAPI routes.
- **Why:** This enforces a strict separation of concerns. The backend teammate building FastAPI endpoints does not need to know PyTorch Geometric or tensor mathematics; they just pass raw JSON to this client and receive a clean fraud probability.
- **Where:** `ml/export/triton_client.py`
- **When:** Week 3, Post-Pipeline Audit 4.

### Decision 010: Dynamic Node Features & Redis Export

- **What:** Decided to dynamically map real-world aggregated account statistics directly into the PyG Node Tensors, and simultaneously export these raw baseline statistics to `redis_node_features.json`.
- **Why:** 1) A GNN cannot effectively detect complex fraud rings using only topology; it requires rich, distinct node histories. 2) The backend requires an instantly accessible O(1) state cache (Redis) to serve the Triton Inference model in <15ms without recalculating global transaction sums.
- **Where:** `ml/preprocessing/graph_builder.py`
- **When:** Week 3, Post-Pipeline Audit 5.

### Decision 011: Artificial Edge Injection for Real-Time Inference

- **What:** Decided to force the FastAPI Triton client to artificially inject the pending transaction into the NumPy edge tensors before sending the payload to the GNN.
- **Why:** In an Edge Classification paradigm, you cannot score an edge that doesn't exist. Since the transaction is pending (not written to the database yet), we must simulate it mathematically inside the localized subgraph so the GNN can "see" the proposed connection and evaluate its fraud probability.
- **Where:** `ml/export/triton_client.py`
- **When:** Week 3, Post-Pipeline Audit 6.

### Decision 012: Unified Mathematical Normalization (Single-Source Scaling)

- **What:** Decided to strictly route all data normalization through the `FeatureEngineer` class and export both node and edge `StandardScaler` objects to disk.
- **Why:** To prevent "Double-Scaler Desyncs". If the backend Triton Client normalizes live JSON transactions using different mean/standard deviation parameters than what the PyTorch GNN was trained on, the mathematical inputs shift drastically, causing the model to incorrectly classify fraud patterns.
- **Where:** `ml/preprocessing/graph_builder.py` & `ml/export/triton_client.py`
- **When:** Week 3, Post-Pipeline Audit 7.

### Decision 013: GPU Acceleration & Automated XAI Validation

- **What:** Decided to force strict GPU (`.to(device)`) tensor mapping globally and embed an automated XAI verification step directly into the CI/CD training orchestrator.
- **Why:** 1) GNNs on Heterogeneous datasets will memory-thrash a CPU; CUDA is required for the low-latency engineering constraint. 2) Unused code becomes dead code. By forcing the Explainer to generate a JSON artifact on every training run, we guarantee the mathematical explainer logic remains synchronized with the model architecture over time.
- **Where:** `ml/train_pipeline.py`
- **When:** Week 3, Post-Pipeline Audit 8.

### Decision 014: Decoupled Cloud Training & Local Inference

- **What:** Decided to separate the Training Phase (Cloud GPU) from the Inference Phase (Local CPU) and generated a colab_training.ipynb notebook to facilitate this.
- **Why:** The local development PC lacks a dedicated CUDA GPU. Training the Graph Neural Network locally on a CPU would take an unacceptably long time. By utilizing a free Google Colab GPU, the model trains in minutes. Because we built the K-Hop Subgraph Extractor earlier, the resulting .pth weights can be downloaded and run in real-time on the local CPU for live demo presentations, perfectly fulfilling the <15ms latency constraint without requiring expensive local hardware.
- **Where:** ml/colab_training.ipynb
- **When:** Week 3, Hardware Restraint Resolution.

### Decision 015: Pandas Memory Downcasting & Secure Cloud Auth

- **What:** Decided to force aggressive Pandas memory downcasting during the Feature Engineering phase and implemented an interactive Kaggle Auth bridge for the Colab deployment.
- **Why:** Google Colab Free Tier enforces a strict 12.7GB System RAM limit. A 4GB raw financial dataset will immediately trigger an OOM crash when Pandas creates intermediate dataframes during `groupby` rolling sum operations. Downcasting integers and floats preemptively prevents this. Furthermore, cloud machines require dynamic API credential injection to fetch raw data without compromising local auth keys.
- **Where:** `ml/preprocessing/feature_engineering.py` & `ml/colab_training.ipynb`
- **When:** Week 3, Cloud Deployment Prep.

### Decision 016: Unified Artifact Zipping for ONNX Migration

- **What:** Decided to write Python logic into the Colab notebook that merges the `export/` directory into the `artifacts/` directory before initiating the cloud download.
- **Why:** The backend Triton Inference server strictly requires the `.onnx` and `.pbtxt` files. Without packaging them into the single cloud-download zip file, the local deployment pipeline would be fundamentally broken. This ensures a seamless "one-click" download that contains everything needed to boot the real-time API.
- **Where:** `ml/colab_training.ipynb`
- **When:** Week 3, Final Migration Architecture Sweep.

### Decision 017: Explicit CUDA VRAM Garbage Collection & Localized Git Blacklisting

- **What:** Decided to manually override PyTorch's lazy memory allocator using `del` and `empty_cache()`, and wrote a strict artifact `.gitignore` inside the `ml/` directory.
- **Why:** 1) To guarantee that a free-tier Google Colab GPU does not OOM crash during the multi-epoch validation loops on a 4GB dataset. 2) To protect the GitHub repository from instantly failing when a developer attempts to push massive generated `.onnx` binaries and processed CSVs.
- **Where:** `ml/train_pipeline.py`, `ml/models/gnn.py`, `ml/.gitignore`
- **When:** Week 3, Pre-Flight Environment Audit.

### Decision 018: Flat Tensor ONNX Wrapper Architecture

- **What:** Decided to wrap the GNN inside a flattened PyTorch `nn.Module` translation layer before initiating the ONNX export, rather than attempting to export the raw PyG dictionaries.
- **Why:** The NVIDIA Triton Inference Server operates on flat C++ HTTP/gRPC arrays. PyTorch Geometric relies on highly nested Python dictionaries. Bypassing this incompatibility via a native translation wrapper ensures the C++ execution engine can seamlessly communicate with the PyTorch logic without raising dimensionality exceptions.
- **Where:** `ml/export/triton_exporter.py`
- **When:** Week 3, Final Inference Architecture Sweep.

### Decision 019: Deterministic Execution & Permanent Audit Logging

- **What:** Decided to upgrade the orchestrator from volatile `print()` statements to dual-channel file logging (`training_run.log`), and forcefully locked the global PyTorch/NumPy RNG seeds to `42`.
- **Why:** Enterprise ML requires absolute auditability and scientific reproducibility. If a model predicts fraud in production, the engineering team must have the permanent training log to prove its initial metrics, and they must be able to retrain the model and achieve the exact same mathematical weights.
- **Where:** `ml/train_pipeline.py`
- **When:** Week 3, Final Enterprise Operations Sweep.

### Decision 020: Defensive Relational Mapping & Metric Zero-Division Patch

- **What:** Decided to replace strict list comprehensions with defensive mapping functions in the graph builder, and enforced zero-division handling in Scikit-Learn evaluation metrics.
- **Why:** Real-world enterprise datasets are messy. A robust machine learning pipeline must dynamically catch and ignore orphaned data (like broken Foreign Keys) rather than suffering a hard crash. Similarly, early-epoch AI behavior naturally results in zero-division math anomalies, which must be systematically suppressed to maintain log integrity.
- **Where:** `ml/preprocessing/graph_builder.py` & `ml/models/gnn.py`
- **When:** Week 3, Ultimate Data Integrity Sweep.

### Decision 021: Hardware-Agnostic PyTorch Serialization

- **What:** Decided to strip all CUDA hardware mappings from the neural network weights prior to binary serialization, and enforced CPU-mapped deserialization globally.
- **Why:** Machine Learning artifacts must be highly portable. A model trained on an advanced cloud GPU must be seamlessly deployable to a local CPU without requiring the backend engineering team to reverse-engineer hardware tensor configurations. This guarantees true "train once, run anywhere" capabilities.
- **Where:** `ml/train_pipeline.py`
- **When:** Week 3, Hardware Portability Sweep.

### Decision 022: Native ONNX Sigmoid Activation

- **What:** Decided to inject a mathematical Sigmoid function directly into the ONNX wrapper compilation, forcing the deployed C++ model to output probabilities rather than training logits.
- **Why:** Training stability requires raw logits (to prevent gradient saturation), but real-time production inference strictly requires understandable probabilities. By hardcoding the Sigmoid directly into the ONNX graph, we ensure the backend API requires zero complex mathematical decoding—it just reads the number and routes the transaction.
- **Where:** `ml/export/triton_exporter.py`
- **When:** Week 3, Ultimate API Metric Alignment Sweep.

### Decision 023: Strict Positional Array Export for Redis

- **What:** Decided to strip human-readable dictionary keys from the Redis feature JSON artifact and enforce a strict positional array schema.
- **Why:** Artificial Intelligence tensors are purely positional arrays. A dictionary introduces a vulnerability where backend parsing logic can accidentally scramble the order of features. By forcing the artifact into strict arrays, we align the backend storage format precisely 1-to-1 with the PyTorch tensor expectations, preventing silent mathematical scaling crashes.
- **Where:** `ml/preprocessing/graph_builder.py`
- **When:** Week 3, Ultimate API Handshake Sweep.

### Decision 024: Pinned Enterprise Build Manifest

- **What:** Decided to strictly lock all dependencies in `requirements.txt` based on the newly expanded architecture.
- **Why:** Cloud machines instantiate from blank slates. Without a comprehensive manifest, Python code referencing advanced modules (like XAI) will trigger fatal import crashes.
- **Where:** `ml/requirements.txt`
- **When:** Week 3, Cloud Provisioning Sweep.

### Decision 025: Subgraph Minibatching for Infinite Scaling

- **What:** Decided to replace Full-Batch GNN training with `NeighborLoader` stochastic minibatching.
- **Why:** Real-world enterprise fraud datasets are gigabytes or terabytes in size and mathematically cannot fit inside standard GPU hardware during convolutional message passing. By keeping the graph on the CPU and streaming local subgraphs to the GPU, we decouple the dataset size from the hardware limits entirely.
- **Where:** `ml/train_pipeline.py` & `ml/models/gnn.py`
- **When:** Week 3, Ultimate Hardware Limit Sweep.
