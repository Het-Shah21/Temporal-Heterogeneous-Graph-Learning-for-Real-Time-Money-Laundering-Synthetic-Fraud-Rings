from kafka import KafkaProducer
import json
import os
from dotenv import load_dotenv

load_dotenv()

producer = KafkaProducer(
    bootstrap_servers=os.getenv("REDPANDA_BROKER", "localhost:9092"),
    value_serializer=lambda value: json.dumps(value).encode("utf-8")
)


def publish_transaction(transaction: dict):
    future = producer.send("transactions", transaction)
    future.get(timeout=10)
    return True