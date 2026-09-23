from fastapi import FastAPI
from backend.app.routes.transactions import router as transaction_router
from backend.app.routes.websocket import router as websocket_router

app = FastAPI(
    title="Fraud Detection API",
    description="Real-time fraud detection backend",
    version="0.1.0"
)

app.include_router(transaction_router)
app.include_router(websocket_router)
@app.get("/")
def root():
    return {
        "message": "Fraud Detection API is running"
    }


@app.get("/health")
def health():
    from backend.app.services.redis_service import check_redis
    from backend.app.services.memgraph_service import check_memgraph

    redis_status = False
    memgraph_status = False

    try:
        redis_status = check_redis()
    except Exception:
        pass

    try:
        memgraph_status = check_memgraph() == 1
    except Exception:
        pass

    overall_status = (
        "healthy"
        if redis_status and memgraph_status
        else "degraded"
    )

    return {
        "status": overall_status,
        "services": {
            "redis": redis_status,
            "memgraph": memgraph_status
        }
    }