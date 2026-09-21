# Technology Stack

## 1. Architecture

```text
Frontend
   |
   v
FastAPI Backend
   |
   v
Redpanda -----> Transaction Consumer
                   |
          +--------+--------+
          |                 |
          v                 v
      Memgraph            Redis
          |                 |
          +--------+--------+
                   |
                   v
             Feature Layer
                   |
                   v
          PyTorch / PyG Model
                   |
                   v
             Fraud Score
                   |
                   v
          FastAPI / WebSocket
                   |
                   v
                Frontend
```

## 2. Backend
- Python 3.11
- FastAPI
- Uvicorn
- python-dotenv
- Kafka-compatible Python client (`kafka-python`)

## 3. Streaming
### Redpanda
Purpose:
- Transaction event streaming
- Kafka-compatible messaging
- Decouples transaction ingestion from processing

Topic:
- `transactions`

## 4. Graph Database
### Memgraph
Purpose:
- Dynamic transaction graph
- User/account nodes
- Transaction relationships
- Graph queries for behavioral features

Connection:
- Bolt
- Default local port: `7687`

## 5. Feature Store / Cache
### Redis
Purpose:
- Transaction storage
- Feature storage
- Fast feature retrieval

Example keys:
```text
transaction:TX006
features:TX006
```

## 6. Machine Learning
Planned:
- scikit-learn for baseline models
- PyTorch
- PyTorch Geometric
- Heterogeneous GNN / GAT
- Temporal graph modeling

Possible baseline:
- Logistic Regression
- Random Forest
- XGBoost if required

## 7. Model Serving
Planned:
- NVIDIA Triton Inference Server

Purpose:
- Model serving
- Standardized inference API
- Separation of model execution from backend API

## 8. Backend API
Planned endpoints:
```text
GET  /
GET  /health
POST /transactions/
GET  /transactions/{id}
GET  /features/{id}
POST /predict
```

WebSocket:
```text
/ws/transactions
```

## 9. Background Processing
Planned:
- Celery for non-critical background tasks
- Explainability jobs
- Heavy graph analysis

## 10. Frontend
Planned:
- Next.js
- React
- TypeScript
- Tailwind CSS
- shadcn/ui
- React Force Graph

## 11. Explainability
Planned:
- PyG Explainer
- Captum where appropriate

## 12. Infrastructure
- Docker
- Docker Compose
- GitHub
- Git feature branches

Current local services:
```text
Redpanda  : 9092
Memgraph  : 7687
Redis     : 6379
FastAPI   : 8000
```
