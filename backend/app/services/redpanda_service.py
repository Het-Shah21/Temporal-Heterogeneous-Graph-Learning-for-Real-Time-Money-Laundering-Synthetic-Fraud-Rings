from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
import os

from dotenv import load_dotenv

load_dotenv()


producer = KafkaProducer(
    bootstrap_servers=os.getenv(
        "REDPANDA_BROKER",
        "localhost:9092"
    ),
    value_serializer=lambda value: json.dumps(value).encode("utf-8")
)


def publish_transaction(transaction: dict):
    try:
        future = producer.send(
            "transactions",
            transaction
        )

        future.get(timeout=10)

        return True

    except KafkaError as error:
        print(f"Redpanda error: {error}")
        return False

def publish_to_dlq(transaction: dict, error: str):
    try:
        dlq_message = {
            "transaction": transaction,
            "error": error
        }

        future = producer.send(
            "fraud_transactions_dlq",
            dlq_message
        )

        future.get(timeout=10)

        print("Transaction published to DLQ.")
        return True

    except Exception as error:
        print(f"DLQ publish error: {error}")
        return False