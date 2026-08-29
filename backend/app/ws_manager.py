import asyncio
import logging
from typing import Any

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.users: dict[str, WebSocket] = {}
        self.admins: set[WebSocket] = set()

    async def connect_user(self, user_id: str, ws: WebSocket) -> None:
        await ws.accept()
        self.users[user_id] = ws

    async def connect_admin(self, ws: WebSocket) -> None:
        await ws.accept()
        self.admins.add(ws)

    def disconnect_user(self, user_id: str) -> None:
        self.users.pop(user_id, None)

    def disconnect_admin(self, ws: WebSocket) -> None:
        self.admins.discard(ws)

    async def broadcast(self, message: dict[str, Any]) -> None:
        all_sockets = list(self.users.values()) + list(self.admins)
        if not all_sockets:
            return
        results = await asyncio.gather(
            *[ws.send_json(message) for ws in all_sockets],
            return_exceptions=True,
        )
        dead_user_ids = [
            uid for uid, ws in self.users.items()
            if isinstance(results[list(self.users.values()).index(ws)], Exception)
        ] if self.users else []
        for uid in dead_user_ids:
            self.disconnect_user(uid)

    async def broadcast_to_admins(self, message: dict[str, Any]) -> None:
        dead: set[WebSocket] = set()
        for ws in list(self.admins):
            try:
                await ws.send_json(message)
            except Exception:
                dead.add(ws)
        self.admins -= dead

    async def send_to_user(self, user_id: str, message: dict[str, Any]) -> None:
        ws = self.users.get(user_id)
        if ws:
            try:
                await ws.send_json(message)
            except Exception:
                self.disconnect_user(user_id)


manager = ConnectionManager()
