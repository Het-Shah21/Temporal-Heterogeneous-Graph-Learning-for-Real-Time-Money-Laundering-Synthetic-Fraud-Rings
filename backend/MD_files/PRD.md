# Product Requirements Document (PRD)
## Temporal Heterogeneous Graph Learning for Real-Time Money Laundering & Synthetic Fraud Rings

### 1. Product Overview
A real-time fraud detection platform that processes financial transactions as they arrive, maintains a dynamic transaction graph, extracts behavioral and temporal features, and uses machine learning/graph learning to identify suspicious transactions and fraud rings.

### 2. Problem Statement
Traditional transaction-level fraud models often analyze individual transactions independently. Modern financial fraud can involve groups of accounts, repeated transfers, circular flows, mule accounts, and synthetic identities. The system should therefore combine transaction-level features with graph relationships and temporal behavior.

### 3. Goals
- Ingest transactions in real time.
- Maintain a dynamic transaction graph.
- Store fast-access transaction and feature data.
- Generate temporal and behavioral features.
- Provide a backend API for transaction submission and fraud scores.
- Support heterogeneous temporal graph learning.
- Provide explainable fraud predictions.
- Display transaction/network activity through a dashboard.

### 4. Core User Flow
1. A transaction is submitted to the FastAPI backend.
2. FastAPI adds a timestamp and publishes the transaction to Redpanda.
3. The transaction consumer reads the event.
4. The transaction is stored in Memgraph.
5. Transaction data is stored in Redis.
6. Behavioral/temporal features are generated.
7. Features are stored in Redis.
8. The ML service consumes the features/graph context.
9. The model produces a fraud/anomaly score.
10. FastAPI/WebSocket exposes the result to the frontend.
11. Explainability information can be generated asynchronously.

### 5. Functional Requirements
#### Transaction Ingestion
- Accept transaction ID, sender, receiver, amount, and related metadata.
- Automatically assign an UTC timestamp when required.
- Publish events to the `transactions` Redpanda topic.

#### Graph Processing
- Represent users/accounts as graph nodes.
- Represent transfers as `SENT` relationships.
- Store transaction ID, amount, and timestamp on relationships.

#### Feature Engineering
Current features:
- Amount
- Sender existence
- Receiver existence
- Sender transaction count
- Total amount sent by sender
- Unique receiver count
- Recent transaction count

Future features:
- Time-windowed transaction velocity
- Average transaction amount
- Amount deviation from sender history
- In/out degree
- Counterparty concentration
- Circular transaction indicators
- Community/ring features

#### Fraud Detection
- Provide a baseline ML model.
- Add a heterogeneous temporal GNN.
- Produce a fraud probability/anomaly score.
- Evaluate using precision, recall, F1, ROC-AUC and PR-AUC where appropriate.

#### Explainability
- Explain important features and graph relationships.
- Keep explanation generation outside the critical low-latency path where possible.

### 6. Non-Functional Requirements
- Real-time or near-real-time processing.
- Modular architecture.
- Docker-based local development.
- Reproducible setup.
- Clear separation between ingestion, storage, feature engineering, ML, and API layers.
- Target low-latency inference path for the final MVP.

### 7. MVP Scope
The MVP should demonstrate:
- Transaction ingestion
- Event streaming
- Graph storage
- Redis feature storage
- Feature generation
- Baseline fraud model
- Temporal/heterogeneous GNN prototype
- Fraud score API
- Basic frontend visualization
- Basic explanation output

### 8. Out of Scope for MVP
- Production-scale deployment
- Real banking integration
- Regulatory certification
- Full identity verification
- High-availability cloud infrastructure
- Automated financial/legal decisions

### 9. Success Criteria
The project is successful when a transaction can travel through the complete pipeline from API ingestion to feature generation and model scoring, with the graph and temporal context available to the ML system.
