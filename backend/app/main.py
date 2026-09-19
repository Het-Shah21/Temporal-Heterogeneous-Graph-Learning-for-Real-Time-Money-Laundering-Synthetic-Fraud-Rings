from fastapi import FastAPI
from backend.app.routes.transactions import router as transaction_router

app = FastAPI(
    title="Fraud Detection API",
    description="Real-time fraud detection backend",
    version="0.1.0"
)

app.include_router(transaction_router)
@app.get("/")
def root():
    return {
        "message": "Fraud Detection API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }