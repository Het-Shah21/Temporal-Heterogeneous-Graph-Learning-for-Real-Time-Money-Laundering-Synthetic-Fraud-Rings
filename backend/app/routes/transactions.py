from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone

from backend.app.models import Transaction, TransactionResponse, PredictionResponse, TransactionFeatures
from backend.app.services.redpanda_service import publish_transaction
from backend.app.services.ml_service import get_ml_feature_vector
from backend.app.services.prediction_service import predict_fraud, ModelUnavailable
from backend.app.services.alert_service import send_fraud_alert
from backend.app.services.transaction_schema import normalize_transaction
from backend.app.services.transaction_schema import TransactionValidationError

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("/", response_model=TransactionResponse)
def create_transaction(transaction: Transaction):
    from backend.app.services.redis_service import redis_client

    transaction_id = transaction.transaction_id
    idempotency_key = f"transaction:accepted:{transaction_id}"

    try:
        # Atomically reserve the transaction ID.
        reserved = redis_client.set(
            idempotency_key,
            "processing",
            nx=True,
            ex=86400
        )

        if not reserved:
            raise HTTPException(
                status_code=409,
                detail="Transaction ID has already been accepted"
            )

        transaction_data = normalize_transaction(transaction.model_dump())

        success = publish_transaction(transaction_data)

        if not success:
            redis_client.delete(idempotency_key)
            raise HTTPException(
                status_code=503,
                detail="Failed to publish transaction to Redpanda"
            )

        # Keep the ID reserved if this update fails, avoiding
        # an immediate duplicate publication on a retry.
        redis_client.set(
            idempotency_key,
            "accepted",
            ex=86400
        )

        return {
            "status": "success",
            "message": "Transaction published successfully",
            "transaction": transaction_data
        }

    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail="Transaction service temporarily unavailable"
        ) from error


@router.get(
    "/{transaction_id}/features",
    response_model=TransactionFeatures
)
def get_transaction_features_api(transaction_id: str):
    from backend.app.services.redis_service import redis_client

    data = redis_client.hgetall(f"features:{transaction_id}")

    if not data:
        raise HTTPException(
            status_code=404,
            detail="Features not found"
        )

    try:
        return {
            "amount": float(data["amount"]),
            "hour_of_day": int(data["hour_of_day"]),
            "s_out_degree": int(data["s_out_degree"]),
            "s_total_sent": float(data["s_total_sent"]),
            "r_in_degree": int(data["r_in_degree"]),
            "r_total_received": float(data["r_total_received"]),
            "time_delta": float(data["time_delta"]),
        }
    except (KeyError, TypeError, ValueError) as error:
        raise HTTPException(status_code=503, detail="Stored feature data is invalid") from error


@router.post(
    "/{transaction_id}/predict",
    response_model=PredictionResponse
)
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

    try:
        features = get_ml_feature_vector(transaction_id, sender_id)
    except ModelUnavailable as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except TransactionValidationError as error:
        raise HTTPException(status_code=503, detail="Stored transaction data is invalid") from error

    if features is None:
        raise HTTPException(
            status_code=404,
            detail="Features not found"
        )

    try:
        prediction = predict_fraud(features)
    except ModelUnavailable as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    # Strict compliance with backend test contract
    if prediction["prediction"] == 1:
        await send_fraud_alert(
            transaction_id,
            prediction["fraud_probability"]
        )

    gnn_result = None
    try:
        from backend.app.services.gnn_service import predict_gnn
        raw_amt = float(transaction_data.get("amount", 1000.0))
        sender_profile = [float(features[2]), float(features[3]), 1.0, 500.0]
        receiver_profile = [1.0, 500.0, float(features[4]), float(features[5])]
        gnn_result = predict_gnn(
            sender_profile=sender_profile,
            receiver_profile=receiver_profile,
            scaled_amount=float(features[0]),
            scaled_time_delta=float(features[6]),
            baseline_xgb_score=prediction["fraud_probability"],
            raw_amount=raw_amt,
        )
    except Exception:
        gnn_result = None

    response_data = {
        "status": "success",
        "transaction_id": transaction_id,
        "prediction": prediction["prediction"],
        "fraud_probability": prediction["fraud_probability"],
    }
    if gnn_result:
        response_data["gnn_probability"] = gnn_result["gnn_probability"]
        response_data["is_alert"] = gnn_result["is_alert"]
        response_data["xai_factors"] = gnn_result["xai_factors"]

    return response_data


@router.post("/screen")
async def screen_transaction_live(payload: dict):
    from ml.predict_service import predict_transaction
    result = predict_transaction(payload)
    if result.get("isAlert"):
        account_id = payload.get("From_Account", "ACC_ALERT")
        score = result.get("modelRiskScore", 0.0)
        try:
            await send_fraud_alert(str(account_id), score)
        except Exception:
            pass
    return result
