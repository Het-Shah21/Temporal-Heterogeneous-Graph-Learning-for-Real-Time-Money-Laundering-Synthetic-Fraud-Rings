"""Replay the original transaction from the Redpanda DLQ."""
import json
import logging
import os
from kafka import KafkaConsumer
from backend.app.services.transaction_consumer import process_transaction

logger = logging.getLogger(__name__)
DLQ_TOPIC = "fraud_transactions_dlq"


def run_replay(max_messages=100):
    consumer = KafkaConsumer(
        DLQ_TOPIC,
        bootstrap_servers=os.getenv("REDPANDA_BROKER", "localhost:9092"),
        group_id=os.getenv("REDPANDA_DLQ_GROUP_ID", "fraud-dlq-replay"),
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        value_deserializer=lambda value: json.loads(value.decode("utf-8")),
    )
    processed = 0
    try:
        for message in consumer:
            envelope = message.value
            transaction = envelope.get("transaction")
            if not transaction:
                logger.error("DLQ message %s has no transaction", message.offset)
                return processed
            process_transaction(transaction)
            consumer.commit()
            processed += 1
            if processed >= max_messages:
                break
    finally:
        consumer.close()
    return processed


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_replay()
