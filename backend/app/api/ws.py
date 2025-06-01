from fastapi import APIRouter, WebSocket

router = APIRouter()

@router.websocket("/progress")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Progress: {data}")
    except Exception as e:
        await websocket.close() 