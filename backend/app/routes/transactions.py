from fastapi import APIRouter
from datetime import datetime, timezone

from backend.app.models import Transaction, TransactionFeatures
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

    data = redis_client.hgetall(f"features:{transaction_id}")

    if not data:
        return {
            "status": "not_found",
            "message": "Features not found"
        }

    return {
        "amount": float(data["amount"]),
        "has_sender": int(data["has_sender"]),
        "has_receiver": int(data["has_receiver"]),
        "sender_transaction_count": int(data["sender_transaction_count"]),
        "total_amount_sent": float(data["total_amount_sent"]),
        "unique_receiver_count": int(data["unique_receiver_count"]),
        "recent_transaction_count": int(data["recent_transaction_count"])
    }