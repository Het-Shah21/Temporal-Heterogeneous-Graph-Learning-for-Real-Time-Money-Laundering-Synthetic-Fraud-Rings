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