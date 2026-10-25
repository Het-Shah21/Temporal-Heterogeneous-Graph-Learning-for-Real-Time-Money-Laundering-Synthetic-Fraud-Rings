from kafka import KafkaConsumer, TopicPartition
from kafka.structs import OffsetAndMetadata
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

    for message in consumer:
        transaction = message.value

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                process_transaction(transaction)

                # Commit only this partition's successfully processed offset.
                consumer.commit(
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

                print(
                    f"Transaction processed successfully. "
                    f"Offset {message.offset} committed."
                )
                break

            except Exception as error:
                print(
                    f"Error processing transaction "
                    f"(attempt {attempt}/{MAX_RETRIES}): {error}"
                )

                if attempt < MAX_RETRIES:
                    print("Retrying the same transaction...")
                    continue

                print("Maximum retries reached. Sending to DLQ...")

                try:
                    dlq_success = publish_to_dlq(
                        transaction,
                        str(error)
                    )
                except Exception as dlq_error:
                    print(f"DLQ publishing failed: {dlq_error}")
                    dlq_success = False

                if dlq_success:
                    print("Failed transaction sent to DLQ.")

                    consumer.commit(
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

                    print("Failed transaction offset committed.")
                else:
                    print(
                        "DLQ publishing failed. "
                        "Offset will not be committed."
                    )
                    # Stop consuming so later messages cannot be
                    # committed past this failed message.
                    return
