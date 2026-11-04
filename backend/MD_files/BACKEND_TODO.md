# Backend TODO

## Current Backend Structure

```text
backend/
├── requirements.txt
└── app/
    ├── __init__.py
    ├── main.py
    ├── routes/
    │   ├── __init__.py
    │   └── transactions.py
    ├── services/
    │   ├── __init__.py
    │   ├── redis_service.py
    │   ├── memgraph_service.py
    │   ├── redpanda_service.py
    │   ├── transaction_consumer.py
    │   └── feature_service.py
    └── models/
        └── __init__.py
```

## Completed

- [x] FastAPI application
- [x] Health endpoint
- [x] Transaction endpoint
- [x] Automatic UTC timestamp for new transactions
- [x] Redpanda producer
- [x] Redpanda transaction topic
- [x] Transaction consumer
- [x] Memgraph transaction storage
- [x] Redis transaction storage
- [x] Feature extraction
- [x] Sender transaction count
- [x] Total amount sent
- [x] Unique receiver count
- [x] Recent transaction count
- [x] Feature storage in Redis
- [x] Docker Compose infrastructure
- [x] Git branch and commits

## TODO — Backend API

- [ ] Add Pydantic transaction model
- [ ] Validate transaction fields
- [ ] Add transaction retrieval endpoint
- [ ] Add feature retrieval endpoint
- [ ] Add fraud prediction endpoint
- [ ] Add proper HTTP error handling
- [ ] Add API response models

Example future model:

```python
class Transaction(BaseModel):
    transaction_id: str
    sender: str
    receiver: str
    amount: float
    timestamp: str | None = None
```

## TODO — Redpanda

- [ ] Move broker configuration to `.env`
- [ ] Add proper producer error handling
- [ ] Add consumer configuration to `.env`
- [ ] Add retry handling
- [ ] Add dead-letter topic if needed

## TODO — Memgraph

- [ ] Add graph indexes/constraints where useful
- [ ] Add more graph relationships
- [ ] Add graph query service
- [ ] Add circular transaction detection
- [ ] Add graph neighborhood extraction for ML

## TODO — Redis

- [ ] Centralize Redis configuration
- [ ] Add feature TTL where appropriate
- [ ] Add feature retrieval API
- [ ] Define stable feature schema
- [ ] Add caching strategy

## TODO — Feature Engineering

Current:
```text
amount
has_sender
has_receiver
sender_transaction_count
total_amount_sent
unique_receiver_count
recent_transaction_count
```

Add:
- [ ] Average transaction amount
- [ ] Transaction velocity
- [ ] Amount deviation
- [ ] Sender/receiver degree
- [ ] Counterparty concentration
- [ ] Time-of-day features
- [ ] Circular transaction indicators
- [ ] Graph neighborhood features

## TODO — ML Integration

- [ ] Define ML feature contract
- [ ] Create model input schema
- [ ] Connect backend to ML inference service
- [ ] Add fraud score response
- [ ] Add model version
- [ ] Add inference latency measurement

## TODO — WebSocket

- [ ] Create WebSocket endpoint
- [ ] Broadcast new transactions
- [ ] Broadcast fraud scores
- [ ] Handle client disconnects
- [ ] Test multiple clients

## TODO — Background Tasks

- [ ] Add Celery if required
- [ ] Move explainability jobs to background
- [ ] Move heavy graph analysis to background
- [ ] Add task status handling

## TODO — Testing

- [ ] Unit tests for services
- [ ] API tests
- [ ] Redis tests
- [ ] Memgraph tests
- [ ] Redpanda integration tests
- [ ] End-to-end transaction test
- [ ] Feature correctness tests
- [ ] Temporal feature edge cases

## TODO — Security & Production Hardening

- [ ] Environment-based secrets
- [ ] Input validation
- [ ] Authentication if required
- [ ] Rate limiting
- [ ] Structured logging
- [ ] Exception handling
- [ ] Health checks for dependencies
- [ ] Metrics/monitoring

## Backend Definition of Done

The backend is considered complete for the MVP when:

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
Feature extraction
   ↓
ML inference
   ↓
Fraud score
   ↓
FastAPI/WebSocket
```

works end-to-end for a test transaction.
