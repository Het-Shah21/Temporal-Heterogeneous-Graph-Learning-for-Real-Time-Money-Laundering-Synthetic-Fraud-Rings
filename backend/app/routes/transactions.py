from fastapi import APIRouter
from backend.app.services.redpanda_service import publish_transaction

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("/")
def create_transaction(transaction: dict):
    publish_transaction(transaction)

    return {
        "status": "success",
        "message": "Transaction published successfully",
        "transaction": transaction
    }