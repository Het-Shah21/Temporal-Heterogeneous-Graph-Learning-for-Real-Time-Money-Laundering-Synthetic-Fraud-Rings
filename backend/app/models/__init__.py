import math
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

    timestamp: str | None = None


class TransactionFeatures(BaseModel):
    amount: float
    has_sender: int
    has_receiver: int
    sender_transaction_count: int
    total_amount_sent: float
    unique_receiver_count: int
    recent_transaction_count: int

class TransactionResponse(BaseModel):
    status: str
    message: str
    transaction: Transaction

class PredictionResponse(BaseModel):
    status: str
    transaction_id: str
    prediction: int
    fraud_probability: float