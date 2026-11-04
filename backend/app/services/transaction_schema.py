"""Canonical transaction contract for API and Kafka event boundaries."""
from datetime import datetime, timezone
import math


class TransactionValidationError(ValueError):
    """Raised when a transaction cannot be normalized safely."""


def _required_string(value, field):
    if not isinstance(value, str) or not value.strip():
        raise TransactionValidationError(f"{field} must be a non-empty string")
    return value.strip()


def _resolve_alias(data, canonical, legacy):
    has_canonical = canonical in data and data[canonical] is not None
    has_legacy = legacy in data and data[legacy] is not None
    if has_canonical and has_legacy and data[canonical] != data[legacy]:
        raise TransactionValidationError(
            f"Conflicting values supplied for {canonical} and {legacy}"
        )
    if has_canonical:
        return data[canonical]
    if has_legacy:
        return data[legacy]
    raise TransactionValidationError(f"Missing required field: {canonical}")


def normalize_transaction(data):
    """Return only the canonical transaction fields.

    Legacy account aliases are accepted for Kafka compatibility, but are not
    part of the public API model and never reach Redis, Memgraph, or features.
    """
    if not isinstance(data, dict):
        raise TransactionValidationError("Transaction message must be an object")

    transaction_id = _required_string(data.get("transaction_id"), "transaction_id")
    sender = _required_string(
        _resolve_alias(data, "sender", "source_account"), "sender"
    )
    receiver = _required_string(
        _resolve_alias(data, "receiver", "destination_account"), "receiver"
    )

    if isinstance(data.get("amount"), bool):
        raise TransactionValidationError("amount must be a finite positive number")
    try:
        amount = float(data["amount"])
    except (KeyError, TypeError, ValueError) as error:
        raise TransactionValidationError("amount must be a finite positive number") from error
    if not math.isfinite(amount) or amount <= 0:
        raise TransactionValidationError("amount must be a finite positive number")

    if "timestamp" not in data or data["timestamp"] is None:
        timestamp = datetime.now(timezone.utc).isoformat()
    else:
        timestamp = data["timestamp"]
        if not isinstance(timestamp, str) or not timestamp.strip():
            raise TransactionValidationError("timestamp must be a valid ISO-8601 string")
        try:
            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError as error:
            raise TransactionValidationError(
                "timestamp must be a valid ISO-8601 string"
            ) from error

    return {
        "transaction_id": transaction_id,
        "sender": sender,
        "receiver": receiver,
        "amount": amount,
        "timestamp": timestamp,
    }
