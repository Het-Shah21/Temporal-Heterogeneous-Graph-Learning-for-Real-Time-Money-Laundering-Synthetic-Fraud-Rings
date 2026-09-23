from kafka import KafkaConsumer
import json
from backend.app.services.memgraph_service import driver
from backend.app.services.redis_service import redis_client
from backend.app.services.feature_service import build_transaction_features
from backend.app.services.feature_service import save_features_to_redis
import os
from dotenv import load_dotenv

load_dotenv()

consumer = KafkaConsumer(
    "transactions",
    bootstrap_servers=os.getenv(
        "REDPANDA_BROKER",
        "localhost:9092"
    ),
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id=os.getenv(
        "REDPANDA_GROUP_ID",
        "fraud-backend"
    ),
    value_deserializer=lambda value: json.loads(value.decode("utf-8"))
)


def save_transaction(transaction):
    with driver.session() as session:
        session.run(
            """
            MERGE (sender:User {id: $sender})
            MERGE (receiver:User {id: $receiver})
            CREATE (sender)-[:SENT {
                transaction_id: $transaction_id,
                amount: $amount,
                timestamp: $timestamp
            }]->(receiver)
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

def consume_transactions():
    print("Transaction consumer started...")

    for message in consumer:
        try:
            transaction = message.value

            print("Received transaction:")
            print(transaction)

            save_transaction(transaction)
            print("Transaction saved to Memgraph!")

            save_transaction_to_redis(transaction)
            print("Transaction saved to Redis!")

            features = build_transaction_features(
                transaction["transaction_id"],
                transaction["sender"]
            )

            print("Extracted features:")
            print(features)

            save_features_to_redis(
                transaction["transaction_id"],
                features
            )

            print("Features saved to Redis!")

        except Exception as error:
            print(f"Error processing transaction: {error}")
            print("Consumer is continuing...")