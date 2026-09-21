from fastapi import APIRouter
from datetime import datetime, timezone

from backend.app.models import Transaction
from backend.app.services.redpanda_service import publish_transaction

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("/")
def create_transaction(transaction: Transaction):
    transaction_data = transaction.model_dump()

    transaction_data["timestamp"] = datetime.now(timezone.utc).isoformat()

    publish_transaction(transaction_data)

    return {
        "status": "success",
        "message": "Transaction published successfully",
        "transaction": transaction_data
    }

@router.get("/{transaction_id}/features")
def get_transaction_features_api(transaction_id: str):
    from backend.app.services.redis_service import redis_client

    features = redis_client.hgetall(f"features:{transaction_id}")

    if not features:
        return {
            "status": "not_found",
            "message": "Features not found"
        }

    return {
        "status": "success",
        "transaction_id": transaction_id,
        "features": features
    }