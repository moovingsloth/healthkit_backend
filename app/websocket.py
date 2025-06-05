from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # 사용자별 연결 관리
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        # 연결 상태 전송
        await self.send_personal_message(
            {"event": "connection_status", "payload": {"connected": True}},
            user_id
        )
        logger.info(f"User {user_id} connected. Active connections: {len(self.active_connections[user_id])}")

    def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"User {user_id} disconnected")

    async def send_personal_message(self, message: dict, user_id: str):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except WebSocketDisconnect:
                    self.disconnect(connection, user_id)
                except Exception as e:
                    logger.error(f"Error sending message to user {user_id}: {str(e)}")

    async def broadcast_health_update(self, user_id: str, health_data: dict):
        await self.send_personal_message(
            {"event": "health_data_update", "payload": health_data},
            user_id
        )

    async def broadcast_concentration_update(self, user_id: str, concentration_data: dict):
        await self.send_personal_message(
            {"event": "concentration_update", "payload": concentration_data},
            user_id
        )

# 싱글톤 인스턴스 생성
manager = ConnectionManager() 