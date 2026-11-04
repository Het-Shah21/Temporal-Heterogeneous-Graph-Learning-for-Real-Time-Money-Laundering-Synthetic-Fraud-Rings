from kafka import KafkaConsumer, TopicPartition
from kafka.structs import OffsetAndMetadata
import json
from backend.app.services.memgraph_service import driver
from backend.app.services.redis_service import redis_client
from backend.app.services.feature_service import build_transaction_features
from backend.app.services.feature_service import save_features_to_redis
import os
import logging
from datetime import datetime, timezone
from dotenv import load_dotenv
from backend.app.services.redpanda_service import publish_to_dlq
from backend.app.services.ml_contract import ArtifactUnavailable
from backend.app.services.transaction_schema import normalize_transaction

load_dotenv()

MAX_RETRIES = int(os.getenv("MAX_TRANSACTION_RETRIES", "3"))
TRANSACTION_TOPIC = "transactions"
DLQ_TOPIC = "fraud_transactions_dlq"
logger = logging.getLogger(__name__)

consumer = None


def get_consumer():
    global consumer
    if consumer is None:
        consumer = KafkaConsumer(
            TRANSACTION_TOPIC,
            bootstrap_servers=os.getenv("REDPANDA_BROKER", "localhost:9092"),
            auto_offset_reset="earliest",
            enable_auto_commit=False,
            group_id=os.getenv("REDPANDA_GROUP_ID", "fraud-backend"),
            value_deserializer=lambda value: json.loads(value.decode("utf-8")),
        )
    return consumer


def save_transaction(transaction):
    with driver.session() as session:
        session.run(
            """
            MERGE (sender:User {id: $sender})
            MERGE (receiver:User {id: $receiver})

            MERGE (sender)-[r:SENT {transaction_id: $transaction_id}]->(receiver)

            SET
                r.amount = $amount,
                r.timestamp = $timestamp
            """,
            sender=transaction["sender"],
            receiver=transaction["receiver"],
            transaction_id=transaction["transaction_id"],
            amount=transaction["amount"],
            timestamp=transaction["timestamp"]
        )

def save_transaction_to_redis(transaction):
    transaction_id = transaction["transaction_id"]

    key = f"transaction:{transaction_id}"

    redis_client.hset(
        key,
        mapping={
            "sender": transaction["sender"],
            "receiver": transaction["receiver"],
            "amount": transaction["amount"],
            "timestamp": transaction["timestamp"]
        }
    )

    # Keep temporary transaction data for 1 hour
    redis_client.expire(key, 3600)

def process_transaction(transaction):
    normalized = normalize_transaction(transaction)
    if isinstance(transaction, dict):
        transaction.clear()
        transaction.update(normalized)
    transaction = normalized
    logger.info("Processing transaction %s", transaction.get("transaction_id"))

    save_transaction(transaction)

    save_transaction_to_redis(transaction)

    try:
        features = build_transaction_features(
            transaction["transaction_id"],
            transaction["sender"]
        )
        if features is not None:
            save_features_to_redis(
                transaction["transaction_id"],
                features
            )
    except ArtifactUnavailable as error:
        # Storage is independent of ML artifacts. Keep the transaction
        # durable and committed; prediction will report 503 until artifacts
        # are installed rather than sending valid transactions to the DLQ.
        logger.warning(
            "Features unavailable for %s: %s",
            transaction.get("transaction_id"),
            error,
        )



def consume_transactions():
    active_consumer = get_consumer()
    try:
      for message in active_consumer:
        transaction = message.value

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                process_transaction(transaction)

                # Commit only this partition's successfully processed offset.
                active_consumer.commit(
                    offsets={
                        TopicPartition(
                            message.topic,
                            message.partition
                        ): OffsetAndMetadata(
                            message.offset + 1,
                            ""
                        )
                    }
                )

                break

            except Exception as error:
                transaction_id = transaction.get("transaction_id") if isinstance(transaction, dict) else "unknown"
                logger.warning("Transaction %s failed (attempt %s/%s): %s", transaction_id, attempt, MAX_RETRIES, error)

                if attempt < MAX_RETRIES:
                    continue

                try:
                    dlq_success = publish_to_dlq(
                        transaction,
                        str(error)
                    )
                except Exception as dlq_error:
                    logger.error("DLQ publishing failed: %s", dlq_error)
                    dlq_success = False

                if dlq_success:
                    active_consumer.commit(
                        offsets={
                            TopicPartition(
                                message.topic,
                                message.partition
                            ): OffsetAndMetadata(
                                message.offset + 1,
                                ""
                            )
                        }
                    )

                else:
                    return
    finally:
      close = getattr(active_consumer, "close", None)
      if close:
          close()
      globals()["consumer"] = None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    consume_transactions()
