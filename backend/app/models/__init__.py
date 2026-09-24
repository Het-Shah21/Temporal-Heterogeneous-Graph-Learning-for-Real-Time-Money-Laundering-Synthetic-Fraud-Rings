from pydantic import BaseModel, Field


class Transaction(BaseModel):
    transaction_id: str = Field(min_length=1)
    sender: str = Field(min_length=1)
    receiver: str = Field(min_length=1)
    amount: float = Field(gt=0)


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