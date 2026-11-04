import math
from datetime import datetime, timezone
from pydantic import BaseModel, Field, field_validator


class Transaction(BaseModel):
    transaction_id: str = Field(min_length=1)
    sender: str = Field(min_length=1)
    receiver: str = Field(min_length=1)
    amount: float = Field(gt=0, allow_inf_nan=False)
    timestamp: str | None = None

    @field_validator("transaction_id", "sender", "receiver")
    @classmethod
    def validate_non_empty_string(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Field cannot contain only whitespace")
        return value

    @field_validator("amount")
    @classmethod
    def validate_finite_amount(cls, value: float) -> float:
        if not math.isfinite(value):
            raise ValueError("Amount must be finite")
        return value

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, value: str | None) -> str | None:
        if value is None:
            return value
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as error:
            raise ValueError("Timestamp must be ISO-8601 formatted") from error
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc).isoformat()

    timestamp: str | None = None


class TransactionFeatures(BaseModel):
    amount: float
    hour_of_day: int
    s_out_degree: int
    s_total_sent: float
    r_in_degree: int
    r_total_received: float
    time_delta: float

class TransactionResponse(BaseModel):
    status: str
    message: str
    transaction: Transaction

class PredictionResponse(BaseModel):
    status: str
    transaction_id: str
    prediction: int
    fraud_probability: float
