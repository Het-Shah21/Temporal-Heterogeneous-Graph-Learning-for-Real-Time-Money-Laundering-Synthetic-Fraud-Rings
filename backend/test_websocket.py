import asyncio
import websockets


async def test():
    uri = "ws://127.0.0.1:8000/ws/alerts"

    async with websockets.connect(uri) as websocket:
        print("WebSocket connected successfully!")
        print("Waiting for fraud alert...")

        while True:
            message = await websocket.recv()
            print("Received alert:")
            print(message)


asyncio.run(test())