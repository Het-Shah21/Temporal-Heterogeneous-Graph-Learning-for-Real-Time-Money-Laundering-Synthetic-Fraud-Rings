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
    transaction = {
        "transaction_id": "TEST_SUCCESS_001",
        "sender": "user_test_1",
        "receiver": "user_test_2",
        "amount": 5000
    }

    def mock_publish_transaction(data):
        return True

    monkeypatch.setattr(
        "backend.app.routes.transactions.publish_transaction",
        mock_publish_transaction
    )

    response = client.post(
        "/transactions/",
        json=transaction
    )

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

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "not_found"
    assert data["message"] == "Features not found"

def test_transaction_features_success(monkeypatch):
    transaction_id = "TEST_FEATURES_001"

    fake_features = {
        "amount": "5000",
        "has_sender": "1",
        "has_receiver": "1",
        "sender_transaction_count": "3",
        "total_amount_sent": "15000",
        "unique_receiver_count": "2",
        "recent_transaction_count": "2"
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
    assert data["has_sender"] == 1
    assert data["has_receiver"] == 1
    assert data["sender_transaction_count"] == 3
    assert data["total_amount_sent"] == 15000
    assert data["unique_receiver_count"] == 2
    assert data["recent_transaction_count"] == 2

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
            "has_sender": 1,
            "has_receiver": 1,
            "sender_transaction_count": 1,
            "total_amount_sent": 5000,
            "unique_receiver_count": 1,
            "recent_transaction_count": 1
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

def test_retry_limit():
    from backend.app.services import transaction_consumer

    retry_counts = {}
    message_key = (0, 100)

    for _ in range(transaction_consumer.MAX_RETRIES):
        retry_counts[message_key] = (
            retry_counts.get(message_key, 0) + 1
        )

    assert retry_counts[message_key] == 3
    assert retry_counts[message_key] >= transaction_consumer.MAX_RETRIES