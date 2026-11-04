from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
import os
import logging

from dotenv import load_dotenv

load_dotenv()


logger = logging.getLogger(__name__)
producer = None
METADATA_TIMEOUT_MS = 5000


def get_producer():
    global producer
    if producer is None:
        producer = KafkaProducer(
            bootstrap_servers=os.getenv("REDPANDA_BROKER", "localhost:9092"),
            value_serializer=lambda value: json.dumps(value).encode("utf-8"),
            acks="all",
            retries=3,
            request_timeout_ms=METADATA_TIMEOUT_MS,
        )
    return producer


def publish_transaction(transaction: dict):
    try:
        future = get_producer().send(
            "transactions",
            transaction
        )

        future.get(timeout=10)

        return True

    except Exception as error:
        logger.warning("Redpanda publish failed: %s", error)
        return False

def publish_to_dlq(transaction: dict, error: str):
    try:
        dlq_message = {
            "transaction": transaction,
            "error": error
        }

        future = get_producer().send(
            "fraud_transactions_dlq",
            dlq_message
        )

        future.get(timeout=10)

        logger.info("Transaction published to DLQ")
        return True

    except Exception as error:
        logger.warning("DLQ publish failed: %s", error)
        return False


def check_redpanda():
    """Check broker metadata for the transaction topic using the shared producer."""
    try:
        partitions = get_producer().partitions_for("transactions")
        return bool(partitions)
    except Exception as error:
        logger.warning("Redpanda metadata check failed: %s", error)
        return False


def close_producer():
    global producer
    if producer is not None:
        producer.close()
        producer = None
