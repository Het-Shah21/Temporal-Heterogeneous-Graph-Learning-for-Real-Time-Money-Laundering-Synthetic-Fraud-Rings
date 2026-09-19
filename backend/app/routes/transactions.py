from fastapi import APIRouter
from backend.app.services.redpanda_service import publish_transaction
from datetime import datetime, timezone

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("/")
def create_transaction(transaction: dict):
    transaction["timestamp"] = datetime.now(timezone.utc).isoformat()

    publish_transaction(transaction)

    return {
        "status": "success",
        "message": "Transaction published successfully",
        "transaction": transaction
    }