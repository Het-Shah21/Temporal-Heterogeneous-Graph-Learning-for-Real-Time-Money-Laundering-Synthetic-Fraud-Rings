import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.app.services.redis_service import redis_client


router = APIRouter()


@router.websocket("/ws/alerts")
async def fraud_alerts(websocket: WebSocket):
    await websocket.accept()

    pubsub = redis_client.pubsub()
    pubsub.subscribe("fraud_alerts")

    print("WebSocket client connected.")

    try:
        while True:
            message = pubsub.get_message(
                ignore_subscribe_messages=True
            )

            if message:
                alert = json.loads(message["data"])
                await websocket.send_json(alert)

            await asyncio.sleep(0.1)

    except WebSocketDisconnect:
        print("WebSocket client disconnected.")

    finally:
        pubsub.close()