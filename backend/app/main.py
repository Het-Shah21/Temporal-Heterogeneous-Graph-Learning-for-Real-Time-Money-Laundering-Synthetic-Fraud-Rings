from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.app.routes.transactions import router as transaction_router
from backend.app.routes.websocket import router as websocket_router


class ServiceHealth(BaseModel):
    redis: bool
    memgraph: bool
    redpanda: bool


class HealthResponse(BaseModel):
    status: str
    services: ServiceHealth


@asynccontextmanager
async def lifespan(_app):
    yield
    from backend.app.services.redpanda_service import close_producer
    from backend.app.services.redis_service import close_redis
    from backend.app.services.memgraph_service import close_memgraph
    close_producer()
    close_redis()
    close_memgraph()


app = FastAPI(
    title="Fraud Detection API",
    description="Real-time fraud detection backend",
    version="0.1.0",
    lifespan=lifespan,
)

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transaction_router)
app.include_router(websocket_router)


@app.get("/")
def root():
    return {
        "message": "Fraud Detection API is running"
    }


@app.get("/health", response_model=HealthResponse)
def health():
    from backend.app.services.redis_service import check_redis
    from backend.app.services.memgraph_service import check_memgraph
    from backend.app.services.redpanda_service import check_redpanda

    redis_status = False
    memgraph_status = False
    redpanda_status = False

    try:
        redis_status = check_redis()
    except Exception:
        pass

    try:
        redpanda_status = check_redpanda()
    except Exception:
        pass

    try:
        memgraph_status = check_memgraph() == 1
    except Exception:
        pass

    overall_status = (
        "healthy"
        if redis_status and memgraph_status and redpanda_status
        else "degraded"
    )

    return {
        "status": overall_status,
        "services": {
            "redis": redis_status,
            "memgraph": memgraph_status,
            "redpanda": redpanda_status,
        }
    }
