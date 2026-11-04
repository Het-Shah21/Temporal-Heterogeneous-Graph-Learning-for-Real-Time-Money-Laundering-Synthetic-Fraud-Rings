import json

from backend.app.services.redis_service import redis_client


async def send_fraud_alert(
    transaction_id: str,
    fraud_probability: float
):
    alert = {
        "type": "fraud_alert",
        "transaction_id": transaction_id,
        "fraud_probability": fraud_probability
    }

    redis_client.publish(
        "fraud_alerts",
        json.dumps(alert)
    )