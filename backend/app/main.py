from fastapi import FastAPI

app = FastAPI(
    title="Fraud Detection API",
    description="Real-time fraud detection backend",
    version="0.1.0"
)


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