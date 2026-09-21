# Master Implementation Plan

## Project
Temporal Heterogeneous Graph Learning for Real-Time Money Laundering & Synthetic Fraud Rings

## 1. Current Status

### Completed
- GitHub repository and feature branch configured.
- Python 3.11 virtual environment created.
- Backend project structure created.
- FastAPI application created.
- Docker Desktop configured.
- Redpanda container running.
- Memgraph container running.
- Redis container running.
- Redpanda `transactions` topic created.
- FastAPI transaction endpoint implemented.
- Transactions published to Redpanda.
- Transaction consumer implemented.
- Transactions stored in Memgraph.
- Transactions stored in Redis.
- Feature service implemented.
- Basic behavioral features implemented.
- Temporal timestamp added to new transactions.
- Recent transaction count implemented.
- Feature vector saved to Redis.
- Changes committed and pushed to `feature/pathik-backend`.

## 2. Phase 1 — Infrastructure
Status: **Completed**

Tasks:
- Docker Compose
- Redpanda
- Memgraph
- Redis
- FastAPI
- Environment configuration
- Git workflow

## 3. Phase 2 — Transaction Pipeline
Status: **Completed**

Flow:
```text
POST /transactions/
        |
        v
FastAPI
        |
        v
Redpanda
        |
        v
Transaction Consumer
        |
        +----> Memgraph
        |
        +----> Redis
        |
        v
Feature Service
        |
        v
Redis
```

## 4. Phase 3 — Feature Engineering
Status: **Partially completed**

Current features:
```text
amount
has_sender
has_receiver
sender_transaction_count
total_amount_sent
unique_receiver_count
recent_transaction_count
```

Next features:
- Average amount
- Transaction velocity
- Amount deviation
- In/out degree
- Receiver concentration
- Time-of-day behavior
- Circular transaction patterns

## 5. Phase 4 — Dataset & Baseline ML
Status: **TODO**

Tasks:
- Select/create fraud transaction dataset.
- Clean data.
- Map transactions to graph entities.
- Create labels.
- Train baseline model.
- Evaluate precision, recall, F1, ROC-AUC and PR-AUC.
- Save model.

## 6. Phase 5 — Heterogeneous Temporal Graph Model
Status: **TODO**

Tasks:
- Define node types.
- Define edge types.
- Define temporal representation.
- Build PyTorch Geometric graph.
- Implement heterogeneous GNN.
- Add temporal features.
- Train model.
- Compare against baseline.

Potential graph:
```text
User ----SENT----> User
User ----OWNS----> Account
Account ----USES----> Device
Account ----LOCATED_AT----> Location
```

## 7. Phase 6 — Model Serving
Status: **TODO**

Tasks:
- Export trained model.
- Configure Triton.
- Create inference interface.
- Connect FastAPI to model service.
- Measure inference latency.

## 8. Phase 7 — Explainability
Status: **TODO**

Tasks:
- Add PyG Explainer/Captum.
- Generate feature importance.
- Identify important graph relationships.
- Run explanations asynchronously.

## 9. Phase 8 — Frontend
Status: **TODO**

Tasks:
- Next.js setup.
- Dashboard.
- Transaction stream.
- Fraud score display.
- Graph visualization.
- Transaction details.
- Explanation panel.

## 10. Phase 9 — Integration
Status: **TODO**

Final flow:
```text
Transaction
   ↓
FastAPI
   ↓
Redpanda
   ↓
Consumer
   ↓
Memgraph + Redis
   ↓
Feature Extraction
   ↓
GNN / Triton
   ↓
Fraud Score
   ↓
FastAPI/WebSocket
   ↓
Dashboard
```

## 11. Three-Week Plan

### Week 1
- Infrastructure
- Streaming
- Graph database
- Redis
- Transaction pipeline
- Initial features

### Week 2
- Dataset
- Baseline ML
- Graph construction
- Temporal GNN
- Model evaluation

### Week 3
- Model serving
- Explainability
- FastAPI integration
- WebSocket
- Frontend dashboard
- End-to-end testing
- Documentation

## 12. Final Deliverables
- Working GitHub repository
- Docker Compose environment
- Real-time transaction pipeline
- Graph database
- Feature store
- Baseline ML model
- Temporal heterogeneous GNN
- Inference API
- Explainability
- Dashboard
- Evaluation results
- Technical documentation
