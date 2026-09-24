from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone

from backend.app.models import Transaction, TransactionResponse
from backend.app.services.redpanda_service import publish_transaction
from backend.app.services.ml_service import get_ml_feature_vector
from backend.app.services.prediction_service import predict_fraud
from backend.app.services.alert_service import send_fraud_alert

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("/", response_model=TransactionResponse)
def create_transaction(transaction: Transaction):
    transaction_data = transaction.model_dump()

    transaction_data["timestamp"] = datetime.now(timezone.utc).isoformat()

    success = publish_transaction(transaction_data)

    if not success:
        raise HTTPException(
            status_code=503,
            detail="Failed to publish transaction to Redpanda"
        )

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

@router.post("/{transaction_id}/predict")
async def predict_transaction(transaction_id: str):
    from backend.app.services.redis_service import redis_client

    transaction_data = redis_client.hgetall(
        f"transaction:{transaction_id}"
    )

    if not transaction_data:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    sender_id = transaction_data["sender"]

    features = get_ml_feature_vector(
        transaction_id,
        sender_id
    )

    if features is None:
        raise HTTPException(
            status_code=404,
            detail="Features not found"
        )

    prediction = predict_fraud(features)
    if prediction["prediction"] == 1:
        await send_fraud_alert(
            transaction_id,
            prediction["fraud_probability"]
        )

    return {
        "status": "success",
        "transaction_id": transaction_id,
        "prediction": prediction["prediction"],
        "fraud_probability": prediction["fraud_probability"]
    }