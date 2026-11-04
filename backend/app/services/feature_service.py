from datetime import datetime, timezone

from backend.app.services.ml_contract import FEATURE_NAMES, load_scaler
from backend.app.services.redis_service import redis_client
from backend.app.services.memgraph_service import driver


def get_transaction_features(transaction_id):
    data = redis_client.hgetall(f"transaction:{transaction_id}")

    if not data:
        return None

    return {
        "amount": float(data["amount"]),
        "timestamp": data["timestamp"],
        "sender": data["sender"],
        "receiver": data["receiver"],
    }



def _parse_timestamp(value):
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def build_transaction_features(transaction_id, sender_id):
    transaction = get_transaction_features(transaction_id)

    if transaction is None:
        return None

    transaction_time = _parse_timestamp(transaction["timestamp"])
    current_timestamp = transaction_time.isoformat()

    with driver.session() as session:
        sender_result = session.run(
            """
            MATCH (sender:User {id: $sender_id})-[r:SENT]->()
            WHERE r.transaction_id <> $transaction_id
              AND datetime(r.timestamp) < datetime($current_timestamp)

            RETURN
                count(r) AS out_degree,
                coalesce(sum(r.amount), 0) AS total_sent,
                max(datetime(r.timestamp)) AS last_sent_at
            """,
            sender_id=sender_id,
            transaction_id=transaction_id,
            current_timestamp=current_timestamp,
        )
        sender_record = sender_result.single()

        receiver_result = session.run(
            """
            MATCH ()-[r:SENT]->(receiver:User {id: $receiver_id})
            WHERE r.transaction_id <> $transaction_id
              AND datetime(r.timestamp) < datetime($current_timestamp)
            RETURN
                count(r) AS in_degree,
                coalesce(sum(r.amount), 0) AS total_received
            """,
            receiver_id=transaction["receiver"],
            transaction_id=transaction_id,
            current_timestamp=current_timestamp,
        )
        receiver_record = receiver_result.single()

    out_degree = int(sender_record["out_degree"] if sender_record else 0)
    total_sent = float(sender_record["total_sent"] if sender_record else 0.0)
    in_degree = int(receiver_record["in_degree"] if receiver_record else 0)
    total_received = float(receiver_record["total_received"] if receiver_record else 0.0)
    last_sent_at = sender_record["last_sent_at"] if sender_record else None
    if last_sent_at is None:
        time_delta = 0.0
    else:
        time_delta = max(0.0, (transaction_time - _parse_timestamp(str(last_sent_at))).total_seconds())

    scaler = load_scaler()
    scaled_amount, scaled_time_delta = scaler.transform(
        [[transaction["amount"], time_delta]]
    )[0]
    return {
        "amount": float(scaled_amount),
        "hour_of_day": transaction_time.hour,
        "s_out_degree": out_degree,
        "s_total_sent": total_sent,
        "r_in_degree": in_degree,
        "r_total_received": total_received,
        "time_delta": float(scaled_time_delta),
    }



def save_features_to_redis(transaction_id, features):
    key = f"features:{transaction_id}"

    redis_client.hset(
        key,
        mapping=features
    )

    # Keep temporary feature data for 1 hour
    redis_client.expire(key, 3600)
