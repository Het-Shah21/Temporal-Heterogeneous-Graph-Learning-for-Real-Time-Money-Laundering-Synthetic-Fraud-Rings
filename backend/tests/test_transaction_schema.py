import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

from backend.app.services.transaction_schema import (
    TransactionValidationError,
    normalize_transaction,
)


def test_normalizes_current_schema_and_ignores_extra_fields():
    result = normalize_transaction({
        "transaction_id": "TX-1",
        "sender": "ACC-1",
        "receiver": "ACC-2",
        "amount": 10,
        "timestamp": "2026-11-03T12:00:00",
        "extra": {"test": True},
    })

    assert result == {
        "transaction_id": "TX-1",
        "sender": "ACC-1",
        "receiver": "ACC-2",
        "amount": 10.0,
        "timestamp": "2026-11-03T12:00:00",
    }


def test_normalizes_legacy_schema():
    result = normalize_transaction({
        "transaction_id": "TX-2",
        "source_account": "ACC-1",
        "destination_account": "ACC-2",
        "amount": 2500.5,
        "timestamp": "2026-11-03T12:00:00",
    })

    assert result["sender"] == "ACC-1"
    assert result["receiver"] == "ACC-2"
    assert result["amount"] == 2500.5


def test_rejects_conflicting_aliases():
    with pytest.raises(TransactionValidationError):
        normalize_transaction({
            "transaction_id": "TX-3",
            "sender": "ACC-1",
            "source_account": "ACC-9",
            "receiver": "ACC-2",
            "amount": 1,
        })


@pytest.mark.parametrize("payload", [
    {"transaction_id": "TX", "receiver": "ACC-2", "amount": 1},
    {"transaction_id": "TX", "sender": "ACC-1", "amount": 1},
    {"sender": "ACC-1", "receiver": "ACC-2", "amount": 1},
    {"transaction_id": "TX", "sender": " ", "receiver": "ACC-2", "amount": 1},
    {"transaction_id": "TX", "sender": "ACC-1", "receiver": "ACC-2", "amount": 0},
    {"transaction_id": "TX", "sender": "ACC-1", "receiver": "ACC-2", "amount": float("nan")},
    {"transaction_id": "TX", "sender": "ACC-1", "receiver": "ACC-2", "amount": float("inf")},
])
def test_rejects_invalid_messages(payload):
        with pytest.raises(TransactionValidationError):
            normalize_transaction(payload)


def test_adds_utc_timestamp_only_when_absent():
    result = normalize_transaction({
        "transaction_id": "TX-4",
        "sender": "ACC-1",
        "receiver": "ACC-2",
        "amount": 1,
    })

    assert result["timestamp"].endswith("+00:00")
