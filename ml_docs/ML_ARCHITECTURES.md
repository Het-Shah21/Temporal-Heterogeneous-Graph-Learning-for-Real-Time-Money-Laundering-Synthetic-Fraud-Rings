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
