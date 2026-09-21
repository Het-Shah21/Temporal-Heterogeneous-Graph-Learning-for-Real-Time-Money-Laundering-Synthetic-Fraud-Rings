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


def get_sender_transaction_count(sender_id):
    with driver.session() as session:
        result = session.run(
            """
            MATCH (sender:User {id: $sender_id})-[r:SENT]->()
            RETURN count(r) AS transaction_count
            """,
            sender_id=sender_id
        )

        record = result.single()
        return record["transaction_count"] if record else 0


def get_total_amount_sent(sender_id):
    with driver.session() as session:
        result = session.run(
            """
            MATCH (sender:User {id: $sender_id})-[r:SENT]->()
            RETURN coalesce(sum(r.amount), 0) AS total_amount
            """,
            sender_id=sender_id
        )

        record = result.single()
        return float(record["total_amount"]) if record else 0.0


def get_unique_receiver_count(sender_id):
    with driver.session() as session:
        result = session.run(
            """
            MATCH (sender:User {id: $sender_id})-[r:SENT]->(receiver:User)
            RETURN count(DISTINCT receiver) AS receiver_count
            """,
            sender_id=sender_id
        )

        record = result.single()
        return record["receiver_count"] if record else 0


def get_recent_transaction_count(sender_id, minutes=10):
    cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=minutes)

    with driver.session() as session:
        result = session.run(
            """
            MATCH (sender:User {id: $sender_id})-[r:SENT]->()
            WHERE r.timestamp IS NOT NULL
            RETURN r.timestamp AS timestamp
            """,
            sender_id=sender_id
        )

        count = 0

        for record in result:
            timestamp = datetime.fromisoformat(record["timestamp"])

            if timestamp >= cutoff_time:
                count += 1

        return count


def build_transaction_features(transaction_id, sender_id):
    transaction_features = get_transaction_features(transaction_id)

    if transaction_features is None:
        return None

    sender_count = get_sender_transaction_count(sender_id)
    total_sent = get_total_amount_sent(sender_id)
    receiver_count = get_unique_receiver_count(sender_id)
    recent_count = get_recent_transaction_count(sender_id)

    transaction_features["sender_transaction_count"] = sender_count
    transaction_features["total_amount_sent"] = total_sent
    transaction_features["unique_receiver_count"] = receiver_count
    transaction_features["recent_transaction_count"] = recent_count

    return transaction_features


def save_features_to_redis(transaction_id, features):
    redis_client.hset(
        f"features:{transaction_id}",
        mapping=features
    )