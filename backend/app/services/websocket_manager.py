from fastapi import WebSocket
from typing import Dict, List
import json
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}
        logger.info("ConnectionManager initialized")

    async def connect(self, websocket: WebSocket, upload_id: int):
        logger.info(f"Attempting to accept WebSocket connection for upload {upload_id}")
        await websocket.accept()
        if upload_id not in self.active_connections:
            self.active_connections[upload_id] = []
        self.active_connections[upload_id].append(websocket)
        logger.info(f"WebSocket connected successfully for upload {upload_id}. Active connections: {len(self.active_connections[upload_id])}")

    def disconnect(self, websocket: WebSocket, upload_id: int):
        if upload_id in self.active_connections:
            self.active_connections[upload_id].remove(websocket)
            if not self.active_connections[upload_id]:
                del self.active_connections[upload_id]
            logger.info(f"WebSocket disconnected for upload {upload_id}. Remaining connections: {len(self.active_connections.get(upload_id, []))}")

    async def send_logs(self, logs: str, upload_id: int):
        if upload_id in self.active_connections:
            message = json.dumps({"logs": logs}) if isinstance(logs, str) else logs
            logger.debug(f"Sending logs to upload {upload_id}: {message[:100]}...")  # Log first 100 chars
            for connection in self.active_connections[upload_id]:
                try:
                    await connection.send_text(message)
                    logger.debug(f"Successfully sent logs to connection for upload {upload_id}")
                except Exception as e:
                    logger.error(f"Error sending logs to WebSocket for upload {upload_id}: {str(e)}")
                    # Remove the connection if it's causing errors
                    self.disconnect(connection, upload_id)

    async def cleanup(self):
        """Clean up all active connections"""
        logger.info(f"Cleaning up all WebSocket connections. Active uploads: {list(self.active_connections.keys())}")
        for upload_id in list(self.active_connections.keys()):
            for connection in self.active_connections[upload_id]:
                try:
                    await connection.close(code=1000, reason="Server shutdown")
                    logger.info(f"Closed WebSocket connection for upload {upload_id}")
                except Exception as e:
                    logger.error(f"Error closing WebSocket connection for upload {upload_id}: {str(e)}")
            self.active_connections[upload_id] = []
        self.active_connections.clear()
        logger.info("All WebSocket connections cleaned up")

# Create a global instance of the connection manager
manager = ConnectionManager() 