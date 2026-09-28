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