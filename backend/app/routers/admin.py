import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from jose import jwt
from sqlalchemy import Integer, cast, delete, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.dependencies import require_admin
from app.models import ContestState, Photo, Vote
from app.schemas import (
    AdminPhotosResponse,
    AdminSessionRequest,
    AdminSessionResponse,
    PhotoAdminItem,
)
from app.ws_manager import manager

router = APIRouter(prefix="/api/admin")


@router.post("/session", response_model=AdminSessionResponse)
async def create_session(body: AdminSessionRequest):
    if body.password != settings.admin_password:
        raise HTTPException(status_code=401, detail="Invalid password")
    exp = datetime.now(tz=timezone.utc) + timedelta(hours=settings.jwt_expiry_hours)
    token = jwt.encode({"sub": "admin", "exp": exp}, settings.jwt_secret, algorithm="HS256")
    return AdminSessionResponse(token=token)


@router.get("/photos", response_model=AdminPhotosResponse, dependencies=[Depends(require_admin)])
async def list_photos(db: AsyncSession = Depends(get_db)):
    rows = await db.execute(
        select(
            Photo.id,
            Photo.user_id,
            Photo.uploaded_at,
            Photo.file_size_kb,
            func.sum(cast(Vote.liked, Integer)).label("like_count"),
            func.sum(cast(~Vote.liked, Integer)).label("skip_count"),
        )
        .join(Vote, Vote.photo_id == Photo.id, isouter=True)
        .where(Photo.is_deleted == False)  # noqa: E712
        .group_by(Photo.id)
        .order_by(Photo.uploaded_at.asc())
    )
    photos = [
        PhotoAdminItem(
            photo_id=row[0],
            user_id=row[1],
            uploaded_at=row[2],
            file_size_kb=row[3],
            like_count=int(row[4] or 0),
            skip_count=int(row[5] or 0),
        )
        for row in rows.all()
    ]
    return AdminPhotosResponse(photos=photos)


@router.delete("/photos/{photo_id}", dependencies=[Depends(require_admin)])
async def delete_photo(photo_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Photo).where(Photo.id == photo_id, Photo.is_deleted == False))  # noqa: E712
    photo = result.scalar_one_or_none()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    photo.is_deleted = True
    photo.data = None  # free bytes from DB
    await db.commit()
    await manager.broadcast({"event": "photo_deleted", "photo_id": str(photo_id)})
    return {"ok": True}


@router.post("/contest/start", dependencies=[Depends(require_admin)])
async def start_contest(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ContestState).where(ContestState.id == 1))
    state = result.scalar_one_or_none()
    if not state or state.phase != "upload":
        raise HTTPException(status_code=409, detail="Contest must be in 'upload' phase to start")

    photo_count = await db.scalar(
        select(func.count()).select_from(Photo).where(Photo.is_deleted == False)  # noqa: E712
    )
    if photo_count < 2:
        raise HTTPException(status_code=409, detail="Нужно хотя бы 2 фотографии для начала конкурса")

    state.phase = "voting"
    state.started_at = datetime.now(tz=timezone.utc)
    await db.commit()
    await manager.broadcast({"event": "contest_started"})
    return {"ok": True}


@router.post("/contest/end", dependencies=[Depends(require_admin)])
async def end_contest(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ContestState).where(ContestState.id == 1))
    state = result.scalar_one_or_none()
    if not state or state.phase != "voting":
        raise HTTPException(status_code=409, detail="Contest must be in 'voting' phase to end")

    state.phase = "finished"
    state.finished_at = datetime.now(tz=timezone.utc)
    await db.commit()
    await manager.broadcast({"event": "contest_finished"})
    return {"ok": True}


@router.post("/contest/restart", dependencies=[Depends(require_admin)])
async def restart_contest(db: AsyncSession = Depends(get_db)):
    await db.execute(delete(Vote))
    await db.execute(delete(Photo))
    await db.execute(text("DELETE FROM users"))
    await db.execute(
        text("UPDATE contest_state SET phase='upload', started_at=NULL, finished_at=NULL WHERE id=1")
    )
    await db.commit()
    await manager.broadcast({"event": "contest_restarted"})
    return {"ok": True}
