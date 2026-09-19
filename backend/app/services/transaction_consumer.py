from kafka import KafkaConsumer
import json
from backend.app.services.memgraph_service import driver
from backend.app.services.redis_service import redis_client


consumer = KafkaConsumer(
    "transactions",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="fraud-backend",
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
                amount: $amount
            }]->(receiver)
            """,
            sender=transaction["sender"],
            receiver=transaction["receiver"],
            transaction_id=transaction["transaction_id"],
            amount=transaction["amount"]
        )

def save_transaction_to_redis(transaction):
    transaction_id = transaction["transaction_id"]

    redis_client.hset(
        f"transaction:{transaction_id}",
        mapping={
            "sender": transaction["sender"],
            "receiver": transaction["receiver"],
            "amount": transaction["amount"]
        }
    )

def consume_transactions():
    print("Transaction consumer started...")

    for message in consumer:
        transaction = message.value

        print("Received transaction:")
        print(transaction)

        save_transaction(transaction)
        print("Transaction saved to Memgraph!")

        save_transaction_to_redis(transaction)
        print("Transaction saved to Redis!")    