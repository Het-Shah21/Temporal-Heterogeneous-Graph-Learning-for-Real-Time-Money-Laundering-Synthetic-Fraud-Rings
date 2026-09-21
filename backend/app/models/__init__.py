from pydantic import BaseModel


class Transaction(BaseModel):
    transaction_id: str
    sender: str
    receiver: str
    amount: float