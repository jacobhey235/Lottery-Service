import asyncio
import uuid

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from jose import JWTError, jwt
from sqlalchemy import select

from app.config import settings
from app.database import AsyncSessionLocal
from app.models import ContestState, User
from app.ws_manager import manager

router = APIRouter()

PING_INTERVAL = 30


@router.websocket("/ws")
async def websocket_endpoint(
    ws: WebSocket,
    user_id: str | None = Query(default=None),
    admin_token: str | None = Query(default=None),
):
    is_admin = False
    validated_user_id: str | None = None

    if admin_token:
        try:
            payload = jwt.decode(admin_token, settings.jwt_secret, algorithms=["HS256"])
            if payload.get("sub") == "admin":
                is_admin = True
        except JWTError:
            await ws.close(code=4001)
            return
    elif user_id:
        try:
            uid = uuid.UUID(user_id)
        except ValueError:
            await ws.close(code=4001)
            return
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User).where(User.id == uid))
            if not result.scalar_one_or_none():
                await ws.close(code=4001)
                return
        validated_user_id = user_id
    else:
        await ws.close(code=4001)
        return

    if is_admin:
        await manager.connect_admin(ws)
    else:
        await manager.connect_user(validated_user_id, ws)

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(ContestState).where(ContestState.id == 1))
        state = result.scalar_one_or_none()
        phase = state.phase if state else "upload"

    await ws.send_json({"event": "phase_sync", "phase": phase})

    ping_task = asyncio.create_task(_ping_loop(ws))

    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        ping_task.cancel()
        if is_admin:
            manager.disconnect_admin(ws)
        elif validated_user_id:
            manager.disconnect_user(validated_user_id)


async def _ping_loop(ws: WebSocket) -> None:
    try:
        while True:
            await asyncio.sleep(PING_INTERVAL)
            await ws.send_json({"event": "ping"})
    except Exception:
        pass
