# ML System Architectures

*Note: This document is built incrementally. As we progress through development, whenever a new system or sub-system is planned, its complete architecture will be documented here BEFORE any code is written.*

**Design Philosophy:** The architectures documented here are designed to be extremely comprehensive, precise, and accurate, yet simple enough that a beginner joining the team could re-implement the entire ML project from scratch just by following this guide. 

Every system will be broken down into clear Input -> Processing -> Output flows, explicitly detailing the exact logic implemented.

---
*(Detailed architectures will be appended here as we begin planning each specific system.)*

## System 1: Data Acquisition & Heterogeneous Graph Construction Pipeline
*(Phase 1)*

**Objective:** The raw IBM AML dataset provides homogeneous transactional data (Account A -> Account B). To meet our project requirement of detecting synthetic identity rings, we must computationally transform this into a **Heterogeneous Graph** by augmenting it with realistic external entities (Devices, IPs) based on transaction patterns, and outputting clean, normalized files.

### 1. Input
- **Source:** IBM AML Dataset (Kaggle/GitHub) CSV files.
- **Raw Schema:** [Timestamp, From_Bank, From_Account, To_Bank, To_Account, Amount_Received, Receiving_Currency, Payment_Format, Is_Laundering]

### 2. Processing (The Logic)
**Step 2.1: Data Ingestion & Cleaning**
- Load the raw CSV into a Pandas DataFrame.
- Sort all transactions strictly by Timestamp to maintain the temporal integrity critical for our GNN.

**Step 2.2: Node Extraction (Homogeneous -> Heterogeneous)**
- *Accounts:* Extract all unique From_Account and To_Account IDs.
- *Heterogeneous Augmentation (Devices & IPs):* 
  - Standard transactions usually lack deep device intelligence. We will apply a deterministic hashing function to the Account_ID and Bank_ID to generate realistic Device_IDs and IP_Addresses.
  - *Fraud Simulation Logic:* If a transaction is marked Is_Laundering = 1, we will force the participating sender/receiver accounts to share the same Device_ID and IP_Address. This accurately models the real-world behavior of synthetic identity rings (mules operating from the same laptop/botnet).

**Step 2.3: Edge Construction**
- Map (Account) -[SENDS]-> (Account) edges using the transaction amounts and timestamps.
- Map (Account) -[USES]-> (Device) and (Account) -[LOGS_IN_FROM]-> (IP) edges based on the augmented data in Step 2.2.

**Step 2.4: Data Validation & Export**
- Assert no data leakage (ensure timestamps strictly increase).
- Check memory footprint.

### 3. Output
- 
odes_account.csv, 
odes_device.csv, 
odes_ip.csv
- edges_transaction.csv, edges_uses.csv, edges_login.csv
- These files are structured perfectly to be read instantly into PyTorch Geometric HeteroData objects in System 2.

## System 2: Feature Engineering & Baseline ML Pipeline (Edge Classification)
*(Phase 1 & Phase 3)*

**Objective:** Before building complex Graph Neural Networks, we must establish a traditional machine learning baseline (XGBoost) to prove the GNN's superiority. Since our labels (Is_Laundering) are tied to transactions (edges) rather than accounts (nodes), this system will engineer tabular features for every transaction and train a baseline classifier.

### 1. Input
- **Source:** Processed files from System 1 (edges_sends.csv).
- **Data Shape:** [src, dst, amount, timestamp, label]

### 2. Processing (The Logic)
**Step 2.1: Feature Engineering (Tabularizing the Graph)**
Traditional ML cannot understand graph topology naturally, so we must manually compute network statistics and attach them to each transaction.
For every transaction (edge) from Account A to Account B, calculate:
- *Transaction Features:* mount, hour_of_day.
- *Sender (Account A) Features:* out_degree (total transactions sent so far), 	otal_amount_sent (cumulative amount sent so far).
- *Receiver (Account B) Features:* in_degree (total transactions received so far), 	otal_amount_received.
- *Velocity Features:* 	ime_since_last_txn_for_sender.

**Step 2.2: Temporal Data Splitting**
- Sort the dataset strictly by 	imestamp.
- **Train Split:** First 70% of chronological transactions.
- **Validation Split:** Next 15%.
- **Test Split:** Final 15%.
*(Random splitting is strictly prohibited as it causes future-data leakage in financial time-series).*

**Step 2.3: Baseline Model Training**
- Initialize an **XGBoost Classifier**.
- Handle extreme class imbalance (fraud is usually < 1%) by setting scale_pos_weight equal to the ratio of negative to positive samples.
- Train the model using the engineered tabular feature matrix.

**Step 2.4: Evaluation**
- Predict on the Test Split.
- Calculate Precision, Recall, F1-Score, and ROC-AUC.

### 3. Output
- 	abular_features.csv (Saved dataset for fast reloading)
- aseline_xgboost.json (The saved model weights)
- aseline_metrics.txt (Log containing our benchmark metrics that the GNN must beat).

## System 3: Heterogeneous Graph Neural Network (The Core AI Brain)
*(Phase 4)*

**Objective:** To replace the traditional XGBoost baseline with an advanced Graph Neural Network capable of natively understanding the multi-entity topology (Accounts, Devices, IPs) of fraud rings. This system predicts fraud at the transaction level (Edge Classification).

### 1. Input
- **Graph Structure:** 
odes_*.csv and edges_*.csv generated from System 1.
- **Node Features:** Tabular features (like rolling degrees and volumes) mapped to PyTorch tensors.

### 2. Processing (The Logic)
**Step 3.1: PyG HeteroData Construction**
- Map the CSV data into PyTorch Geometric's native HeteroData structure.
- Define Node Types: ['account', 'device', 'ip']
- Define Edge Types: [('account', 'sends', 'account'), ('account', 'uses', 'device'), ('account', 'logs_in', 'ip')]

**Step 3.2: The GNN Architecture (HGT - Heterogeneous Graph Transformer)**
- Initialize a Multi-layer HGTConv (or HeteroConv wrapped SAGEConv) neural network.
- *Message Passing:* The GNN routes information not just between accounts, but pulls risk signals from connected Devices and IPs. (e.g., If IP_X is connected to 5 fraudulent accounts, that risk flows into Account A during the message passing phase).

**Step 3.3: Edge Classification Head (The Predictor)**
- Since fraud is defined by a transaction (an edge), the GNN outputs updated node embeddings for Account A (Sender) and Account B (Receiver).
- We extract the final embedding of A and B, concatenate them with the transaction mount and 	ime_delta, and pass this combined vector through an MLP (Multi-Layer Perceptron) to output a final probability score (0.0 to 1.0).

**Step 3.4: Scalable Batching & Training**
- Graphs are massive. We cannot load millions of nodes into GPU memory at once.
- We will use PyG's NeighborLoader to sample localized *k-hop subgraphs* for each transaction in the batch.
- Loss Function: Binary Cross Entropy with Logits (BCEWithLogitsLoss).
- Optimizer: AdamW.

### 3. Output
- gnn_model.pth: The trained PyTorch model weights.
- gnn_metrics.json: The final evaluation metrics (Precision, Recall, ROC-AUC) to compare against our System 2 baseline.

## System 4: Explainability (XAI) & Triton Deployment Pipeline
*(Phase 5)*

**Objective:** A fraud score is useless for compliance without an auditable reason. This system computes the exact subgraph elements that triggered a high fraud probability. Furthermore, it freezes and exports the model into an optimized format suitable for sub-15ms real-time inference.

### 1. Input
- **Trained Model:** gnn_model.pth from System 3.
- **Inference Graph:** A specific k-hop PyG HeteroData subgraph surrounding a live transaction.

### 2. Processing (The Logic)
**Step 4.1: XAI (Explainability Engine)**
- Integrate PyTorch Geometric's Explainer module.
- We will utilize CaptumExplainer (Integrated Gradients / Shapley Value approximation) to evaluate the model's prediction.
- *Logic:* The explainer will output an edge_mask (a weight from 0 to 1 for every edge in the subgraph) and a 
ode_mask. 
- We will filter this mask to extract the Top 3 highest-weighted edges (e.g., showing that the transaction was flagged specifically because of a shared Device edge).

**Step 4.2: ONNX Model Conversion (Dynamic Axes)**
- NVIDIA Triton Inference Server requires highly optimized models. PyTorch's default .pth is too slow for <15ms execution.
- We will trace the PyTorch GNN and export it to the ONNX (.onnx) format.
- *Crucial Logic:* Graph sizes (nodes/edges) change with every transaction. We must explicitly define **Dynamic Axes** during the ONNX export so Triton knows the tensor dimensions will fluctuate in real-time.

**Step 4.3: Triton Config Generation**
- Generate the strict config.pbtxt required by Triton.
- Map the ONNX input names to Triton inputs, specifying TYPE_FP32 and TYPE_INT64 with dynamic dimensions [-1, -1].

### 3. Output
- explainer.py: A module returning a structured JSON of human-readable fraud reasons.
- model.onnx: The ultra-fast, frozen compute graph.
- config.pbtxt: The Triton deployment configuration.
