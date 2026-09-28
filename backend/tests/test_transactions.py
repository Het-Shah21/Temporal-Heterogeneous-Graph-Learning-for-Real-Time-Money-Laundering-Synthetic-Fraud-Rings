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