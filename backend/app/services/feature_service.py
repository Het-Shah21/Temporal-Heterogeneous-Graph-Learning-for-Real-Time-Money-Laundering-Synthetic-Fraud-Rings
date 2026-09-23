from backend.app.services.redis_service import redis_client
from backend.app.services.memgraph_service import driver
from datetime import datetime, timezone, timedelta


def get_transaction_features(transaction_id):
    data = redis_client.hgetall(f"transaction:{transaction_id}")

    if not data:
        return None

    return {
        "amount": float(data["amount"]),
        "has_sender": 1,
        "has_receiver": 1
    }


def build_transaction_features(transaction_id, sender_id):
    transaction_features = get_transaction_features(transaction_id)

    if transaction_features is None:
        return None

    cutoff_time = (
        datetime.now(timezone.utc) - timedelta(minutes=10)
    ).isoformat()

    with driver.session() as session:
        result = session.run(
            """
            MATCH (sender:User {id: $sender_id})-[r:SENT]->(receiver:User)

            RETURN
                count(r) AS sender_transaction_count,
                coalesce(sum(r.amount), 0) AS total_amount_sent,
                count(DISTINCT receiver) AS unique_receiver_count,
                sum(
                    CASE
                        WHEN r.timestamp >= $cutoff_time
                        THEN 1
                        ELSE 0
                    END
                ) AS recent_transaction_count
            """,
            sender_id=sender_id,
            cutoff_time=cutoff_time
        )

        record = result.single()

        if record:
            transaction_features["sender_transaction_count"] = (
                record["sender_transaction_count"]
            )

            transaction_features["total_amount_sent"] = float(
                record["total_amount_sent"]
            )

            transaction_features["unique_receiver_count"] = (
                record["unique_receiver_count"]
            )

            transaction_features["recent_transaction_count"] = (
                record["recent_transaction_count"] or 0
            )

        else:
            transaction_features["sender_transaction_count"] = 0
            transaction_features["total_amount_sent"] = 0.0
            transaction_features["unique_receiver_count"] = 0
            transaction_features["recent_transaction_count"] = 0

    return transaction_features


def save_features_to_redis(transaction_id, features):
    redis_client.hset(
        f"features:{transaction_id}",
        mapping=features
    )