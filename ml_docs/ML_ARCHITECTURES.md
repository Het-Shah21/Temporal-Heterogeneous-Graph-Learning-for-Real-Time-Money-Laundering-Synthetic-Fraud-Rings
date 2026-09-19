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
