import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[2])
)

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_negative_amount_rejected():
    transaction = {
        "transaction_id": "TEST001",
        "sender": "user_1",
        "receiver": "user_2",
        "amount": -500
    }

    response = client.post(
        "/transactions/",
        json=transaction
    )

    assert response.status_code == 422


def test_empty_sender_rejected():
    transaction = {
        "transaction_id": "TEST002",
        "sender": "",
        "receiver": "user_2",
        "amount": 500
    }

    response = client.post(
        "/transactions/",
        json=transaction
    )

    assert response.status_code == 422


def test_create_transaction_success(monkeypatch):
    from backend.app.routes import transactions

    class FakeRedis:
        def set(self, key, value, nx=False, ex=None):
            return True

        def delete(self, key):
            return 1

    transaction = {
        "transaction_id": "TEST_SUCCESS_001",
        "sender": "user_test_1",
        "receiver": "user_test_2",
        "amount": 5000
    }

    def mock_publish_transaction(data):
        return True

    monkeypatch.setattr(
        "backend.app.services.redis_service.redis_client",
        FakeRedis()
    )
    monkeypatch.setattr(
        transactions,
        "publish_transaction",
        mock_publish_transaction
    )

    response = client.post("/transactions/", json=transaction)

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "success"
    assert data["message"] == "Transaction published successfully"
    assert data["transaction"]["transaction_id"] == "TEST_SUCCESS_001"
    assert data["transaction"]["sender"] == "user_test_1"
    assert data["transaction"]["receiver"] == "user_test_2"
    assert data["transaction"]["amount"] == 5000
    assert "timestamp" in data["transaction"]


def test_prediction_transaction_not_found():
    response = client.post(
        "/transactions/NON_EXISTENT_TX/predict"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Transaction not found"

def test_prediction_success(monkeypatch):
    transaction_id = "TEST_PREDICT_001"

    fake_transaction = {
        "sender": "user_test_1"
    }

    fake_features = [
        5000,
        1,
        1,
        2,
        10000,
        2,
        2
    ]

    fake_prediction = {
        "prediction": 1,
        "fraud_probability": 0.85
    }

    class FakeRedis:
        def hgetall(self, key):
            return fake_transaction

    import backend.app.services.redis_service as redis_service

    monkeypatch.setattr(
        redis_service,
        "redis_client",
        FakeRedis()
    )

    monkeypatch.setattr(
        "backend.app.routes.transactions.get_ml_feature_vector",
        lambda transaction_id, sender_id: fake_features
    )

    monkeypatch.setattr(
        "backend.app.routes.transactions.predict_fraud",
        lambda features: fake_prediction
    )

    async def mock_send_fraud_alert(transaction_id, fraud_probability):
        pass

    monkeypatch.setattr(
        "backend.app.routes.transactions.send_fraud_alert",
        mock_send_fraud_alert
    )

    response = client.post(
        f"/transactions/{transaction_id}/predict"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"
    assert data["transaction_id"] == transaction_id
    assert data["prediction"] == 1
    assert data["fraud_probability"] == 0.85

def test_prediction_normal_transaction(monkeypatch):
    transaction_id = "TEST_PREDICT_NORMAL_001"

    fake_transaction = {
        "sender": "user_normal"
    }

    fake_features = [
        1000,
        1,
        1,
        1,
        1000,
        1,
        1
    ]

    fake_prediction = {
        "prediction": 0,
        "fraud_probability": 0.10
    }

    class FakeRedis:
        def hgetall(self, key):
            return fake_transaction

    import backend.app.services.redis_service as redis_service

    monkeypatch.setattr(
        redis_service,
        "redis_client",
        FakeRedis()
    )

    monkeypatch.setattr(
        "backend.app.routes.transactions.get_ml_feature_vector",
        lambda transaction_id, sender_id: fake_features
    )

    monkeypatch.setattr(
        "backend.app.routes.transactions.predict_fraud",
        lambda features: fake_prediction
    )

    alert_called = False

    async def mock_send_fraud_alert(transaction_id, fraud_probability):
        nonlocal alert_called
        alert_called = True

    monkeypatch.setattr(
        "backend.app.routes.transactions.send_fraud_alert",
        mock_send_fraud_alert
    )

    response = client.post(
        f"/transactions/{transaction_id}/predict"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"
    assert data["transaction_id"] == transaction_id
    assert data["prediction"] == 0
    assert data["fraud_probability"] == 0.10

    assert alert_called is False

def test_transaction_features_not_found():
    response = client.get(
        "/transactions/NON_EXISTENT_TX/features"
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Features not found"

def test_transaction_features_success(monkeypatch):
    transaction_id = "TEST_FEATURES_001"

    fake_features = {
        "amount": "5000",
        "hour_of_day": "10",
        "s_out_degree": "3",
        "s_total_sent": "15000",
        "r_in_degree": "2",
        "r_total_received": "12000",
        "time_delta": "60"
    }

    class FakeRedis:
        def hgetall(self, key):
            assert key == f"features:{transaction_id}"
            return fake_features

    import backend.app.services.redis_service as redis_service

    monkeypatch.setattr(
        redis_service,
        "redis_client",
        FakeRedis()
    )

    response = client.get(
        f"/transactions/{transaction_id}/features"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["amount"] == 5000
    assert data["hour_of_day"] == 10
    assert data["s_out_degree"] == 3
    assert data["s_total_sent"] == 15000
    assert data["r_in_degree"] == 2
    assert data["r_total_received"] == 12000
    assert data["time_delta"] == 60

def test_process_transaction_success(monkeypatch):
    from backend.app.services import transaction_consumer

    transaction = {
        "transaction_id": "TEST_PROCESS_001",
        "sender": "user_test_1",
        "receiver": "user_test_2",
        "amount": 5000,
        "timestamp": "2026-09-29T10:00:00+00:00"
    }

    calls = []

    monkeypatch.setattr(
        transaction_consumer,
        "save_transaction",
        lambda data: calls.append("memgraph")
    )

    monkeypatch.setattr(
        transaction_consumer,
        "save_transaction_to_redis",
        lambda data: calls.append("transaction_redis")
    )

    monkeypatch.setattr(
        transaction_consumer,
        "build_transaction_features",
        lambda transaction_id, sender_id: {
            "amount": 5000,
            "hour_of_day": 10,
            "s_out_degree": 1,
            "s_total_sent": 5000,
            "r_in_degree": 1,
            "r_total_received": 5000,
            "time_delta": 0
        }
    )

    monkeypatch.setattr(
        transaction_consumer,
        "save_features_to_redis",
        lambda transaction_id, features: calls.append("features_redis")
    )

    transaction_consumer.process_transaction(transaction)

    assert calls == [
        "memgraph",
        "transaction_redis",
        "features_redis"
    ]

def test_process_transaction_failure(monkeypatch):
    from backend.app.services import transaction_consumer

    transaction = {
        "transaction_id": "TEST_PROCESS_FAIL_001",
        "sender": "user_test_1",
        "receiver": "user_test_2",
        "amount": 5000,
        "timestamp": "2026-09-30T10:00:00+00:00"
    }

    def failing_save_transaction(data):
        raise Exception("Memgraph connection failed")

    monkeypatch.setattr(
        transaction_consumer,
        "save_transaction",
        failing_save_transaction
    )

    try:
        transaction_consumer.process_transaction(transaction)
        assert False, "Expected process_transaction to fail"
    except Exception as error:
        assert str(error) == "Memgraph connection failed"


def test_retry_limit(monkeypatch):
    from backend.app.services import transaction_consumer

    process_calls = []
    dlq_calls = []
    commit_calls = []

    class FakeMessage:
        topic = "transactions"
        partition = 0
        offset = 100
        value = {
            "transaction_id": "TX_RETRY_TEST",
            "sender": "user_1",
            "receiver": "user_2",
            "amount": 100,
            "timestamp": "2026-10-24T00:00:00+00:00"
        }

    class FakeConsumer:
        def __iter__(self):
            yield FakeMessage()

        def commit(self, offsets=None):
            commit_calls.append(offsets)

    def fail_processing(transaction):
        process_calls.append(transaction)
        raise RuntimeError("Simulated processing failure")

    def successful_dlq(transaction, error):
        dlq_calls.append((transaction, error))
        return True

    monkeypatch.setattr(
        transaction_consumer,
        "consumer",
        FakeConsumer()
    )
    monkeypatch.setattr(
        transaction_consumer,
        "process_transaction",
        fail_processing
    )
    monkeypatch.setattr(
        transaction_consumer,
        "publish_to_dlq",
        successful_dlq
    )

    transaction_consumer.consume_transactions()

    assert len(process_calls) == transaction_consumer.MAX_RETRIES
    assert len(dlq_calls) == 1
    assert len(commit_calls) == 1
    assert dlq_calls[0][0]["transaction_id"] == "TX_RETRY_TEST"


def test_publish_to_dlq(monkeypatch):
    from backend.app.services import redpanda_service

    sent_messages = []

    class FakeFuture:
        def get(self, timeout):
            return True

    class FakeProducer:
        def send(self, topic, message):
            sent_messages.append((topic, message))
            return FakeFuture()

    monkeypatch.setattr(
        redpanda_service,
        "producer",
        FakeProducer()
    )

    transaction = {
        "transaction_id": "TEST_DLQ_001",
        "sender": "user_failed",
        "receiver": "user_receiver",
        "amount": 10000
    }

    result = redpanda_service.publish_to_dlq(
        transaction,
        "Memgraph connection failed"
    )

    assert result is True

    assert len(sent_messages) == 1

    topic, message = sent_messages[0]

    assert topic == "fraud_transactions_dlq"
    assert message["transaction"] == transaction
    assert message["error"] == "Memgraph connection failed"

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

def test_publish_to_dlq_failure(monkeypatch):
    from backend.app.services import redpanda_service

    class FakeFuture:
        def get(self, timeout):
            raise Exception("Redpanda unavailable")

    class FakeProducer:
        def send(self, topic, message):
            return FakeFuture()

    monkeypatch.setattr(
        redpanda_service,
        "producer",
        FakeProducer()
    )

    transaction = {
        "transaction_id": "TEST_DLQ_FAIL_001",
        "sender": "failed_sender",
        "receiver": "failed_receiver",
        "amount": 5000
    }

    result = redpanda_service.publish_to_dlq(
        transaction,
        "Processing failed"
    )

    assert result is False


def test_whitespace_only_sender_rejected():
    response = client.post(
        "/transactions/",
        json={
            "transaction_id": "TX_INVALID_01",
            "sender": "   ",
            "receiver": "user_2",
            "amount": 100
        }
    )
    assert response.status_code == 422


def test_whitespace_only_transaction_id_rejected():
    response = client.post(
        "/transactions/",
        json={
            "transaction_id": "   ",
            "sender": "user_1",
            "receiver": "user_2",
            "amount": 100
        }
    )
    assert response.status_code == 422


def test_zero_amount_rejected():
    response = client.post(
        "/transactions/",
        json={
            "transaction_id": "TX_INVALID_02",
            "sender": "user_1",
            "receiver": "user_2",
            "amount": 0
        }
    )
    assert response.status_code == 422


def test_negative_amount_rejected_again():
    response = client.post(
        "/transactions/",
        json={
            "transaction_id": "TX_INVALID_03",
            "sender": "user_1",
            "receiver": "user_2",
            "amount": -100
        }
    )
    assert response.status_code == 422


def test_dlq_failure_does_not_commit_offset(monkeypatch):
    from backend.app.services import transaction_consumer

    process_calls = []
    commit_calls = []

    class FakeMessage:
        topic = "transactions"
        partition = 0
        offset = 101
        value = {
            "transaction_id": "TX_DLQ_FAILURE",
            "sender": "user_1",
            "receiver": "user_2",
            "amount": 100,
            "timestamp": "2026-10-24T00:00:00+00:00"
        }

    class FakeConsumer:
        def __iter__(self):
            yield FakeMessage()

        def commit(self, offsets=None):
            commit_calls.append(offsets)

    def fail_processing(transaction):
        process_calls.append(transaction)
        raise RuntimeError("Simulated database failure")

    def fail_dlq(transaction, error):
        return False

    monkeypatch.setattr(
        transaction_consumer,
        "consumer",
        FakeConsumer()
    )
    monkeypatch.setattr(
        transaction_consumer,
        "process_transaction",
        fail_processing
    )
    monkeypatch.setattr(
        transaction_consumer,
        "publish_to_dlq",
        fail_dlq
    )

    transaction_consumer.consume_transactions()

    assert len(process_calls) == transaction_consumer.MAX_RETRIES
    assert len(commit_calls) == 0

def test_successful_processing_commits_offset_once(monkeypatch):
    from backend.app.services import transaction_consumer
    from kafka import TopicPartition
    from kafka.structs import OffsetAndMetadata

    process_calls = []
    commit_calls = []
    dlq_calls = []

    class FakeMessage:
        topic = "transactions"
        partition = 0
        offset = 102
        value = {
            "transaction_id": "TX_SUCCESS_TEST",
            "sender": "user_1",
            "receiver": "user_2",
            "amount": 100,
            "timestamp": "2026-10-24T00:00:00+00:00"
        }

    class FakeConsumer:
        def __iter__(self):
            yield FakeMessage()

        def commit(self, offsets=None):
            commit_calls.append(offsets)

    def successful_processing(transaction):
        process_calls.append(transaction)

    def unexpected_dlq(transaction, error):
        dlq_calls.append(transaction)
        return True

    monkeypatch.setattr(
        transaction_consumer, "consumer", FakeConsumer()
    )
    monkeypatch.setattr(
        transaction_consumer, "process_transaction",
        successful_processing
    )
    monkeypatch.setattr(
        transaction_consumer, "publish_to_dlq", unexpected_dlq
    )

    transaction_consumer.consume_transactions()

    assert len(process_calls) == 1
    assert len(commit_calls) == 1
    assert len(dlq_calls) == 0

    committed = commit_calls[0]
    tp = TopicPartition("transactions", 0)
    assert committed[tp] == OffsetAndMetadata(103, "")



def test_duplicate_transaction_id_rejected(monkeypatch):
    from backend.app.routes import transactions

    accepted_ids = set()
    publish_calls = []

    class FakeRedis:
        def set(self, key, value, nx=False, ex=None):
            if nx and key in accepted_ids:
                return None
            accepted_ids.add(key)
            return True

        def delete(self, key):
            accepted_ids.discard(key)

    def mock_publish_transaction(data):
        publish_calls.append(data["transaction_id"])
        return True

    monkeypatch.setattr(
        "backend.app.services.redis_service.redis_client",
        FakeRedis()
    )
    monkeypatch.setattr(
        transactions,
        "publish_transaction",
        mock_publish_transaction
    )

    transaction = {
        "transaction_id": "DUPLICATE_TEST_001",
        "sender": "user_test_1",
        "receiver": "user_test_2",
        "amount": 500
    }

    first_response = client.post("/transactions/", json=transaction)
    second_response = client.post("/transactions/", json=transaction)

    assert first_response.status_code == 200
    assert second_response.status_code == 409
    assert len(publish_calls) == 1


def test_create_transaction_redis_unavailable(monkeypatch):
    from backend.app.routes import transactions

    class FailingRedis:
        def set(self, *args, **kwargs):
            raise ConnectionError("Redis unavailable")

    publish_calls = []

    def mock_publish_transaction(data):
        publish_calls.append(data)
        return True

    monkeypatch.setattr(
        "backend.app.services.redis_service.redis_client",
        FailingRedis()
    )
    monkeypatch.setattr(
        transactions,
        "publish_transaction",
        mock_publish_transaction
    )

    response = client.post(
        "/transactions/",
        json={
            "transaction_id": "TX_REDIS_DOWN",
            "sender": "user_1",
            "receiver": "user_2",
            "amount": 100
        }
    )

    assert response.status_code == 503
    assert publish_calls == []


def test_baseline_feature_contract_order():
    from backend.app.services.ml_contract import FEATURE_NAMES

    assert FEATURE_NAMES == [
        "amount",
        "hour_of_day",
        "s_out_degree",
        "s_total_sent",
        "r_in_degree",
        "r_total_received",
        "time_delta",
    ]


def test_missing_xgboost_artifact_is_unavailable(monkeypatch, tmp_path):
    from backend.app.services import prediction_service

    monkeypatch.setattr(prediction_service, "model", None)
    monkeypatch.setattr(
        prediction_service,
        "MODEL_PATH",
        tmp_path / "missing-baseline_xgboost.json",
    )

    try:
        prediction_service.predict_fraud([1, 2, 3, 4, 5, 6, 7])
        assert False, "Expected missing artifact to be reported"
    except prediction_service.ModelUnavailable:
        pass
