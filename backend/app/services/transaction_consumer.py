from kafka import KafkaConsumer
import json
from backend.app.services.memgraph_service import driver
from backend.app.services.redis_service import redis_client
from backend.app.services.feature_service import build_transaction_features
from backend.app.services.feature_service import save_features_to_redis
import os
from dotenv import load_dotenv
from backend.app.services.redpanda_service import publish_to_dlq

MAX_RETRIES = 3

load_dotenv()

consumer = KafkaConsumer(
    "transactions",
    bootstrap_servers=os.getenv(
        "REDPANDA_BROKER",
        "localhost:9092"
    ),
    auto_offset_reset="earliest",
    enable_auto_commit=False,
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

def consume_transactions():
    print("Transaction consumer started...")

    retry_counts = {}

    for message in consumer:
        message_key = (
            message.partition,
            message.offset
        )

        try:
            transaction = message.value

            process_transaction(transaction)

            # Processing succeeded, so commit the offset
            consumer.commit()

            print("Transaction offset committed!")

            # Clear retry counter after successful processing
            retry_counts.pop(message_key, None)

        except Exception as error:
            retry_counts[message_key] = (
                retry_counts.get(message_key, 0) + 1
            )

            retry_count = retry_counts[message_key]

            print(
                f"Error processing transaction "
                f"(attempt {retry_count}/{MAX_RETRIES}): {error}"
            )

            if retry_count >= MAX_RETRIES:
                print(
                    f"Maximum retries reached for "
                    f"partition={message.partition}, "
                    f"offset={message.offset}"
                )

                dlq_success = publish_to_dlq(
                    transaction,
                    str(error)
                )

                if dlq_success:
                    print("Failed transaction sent to DLQ.")
                    consumer.commit()
                    print("Failed transaction offset committed.")
                else:
                    print(
                        "Failed to publish transaction to DLQ. "
                        "Offset will not be committed."
                    )

                retry_counts.pop(message_key, None)

            else:
                print("Retrying transaction...")