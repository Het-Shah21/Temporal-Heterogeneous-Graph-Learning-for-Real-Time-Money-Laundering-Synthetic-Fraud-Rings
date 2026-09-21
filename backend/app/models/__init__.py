from pydantic import BaseModel


class Transaction(BaseModel):
    transaction_id: str
    sender: str
    receiver: str
    amount: float

class TransactionFeatures(BaseModel):
    amount: float
    has_sender: int
    has_receiver: int
    sender_transaction_count: int
    total_amount_sent: float
    unique_receiver_count: int
    recent_transaction_count: int