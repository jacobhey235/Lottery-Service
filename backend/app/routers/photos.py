import os
import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from fastapi.responses import FileResponse
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models import ContestState, Photo, User

router = APIRouter()


@router.get("/api/photos/{photo_id}/image")
async def serve_photo(
    photo_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    # Accept user_id via header OR query param (query needed for <img> tags)
    x_user_id: str | None = Header(default=None, alias="X-User-ID"),
    user_id: str | None = Query(default=None),
    # Admin can access via token
    admin_token: str | None = Query(default=None),
):
    state_result = await db.execute(select(ContestState).where(ContestState.id == 1))
    state = state_result.scalar_one_or_none()
    phase = state.phase if state else "upload"

    photo_result = await db.execute(
        select(Photo).where(Photo.id == photo_id, Photo.is_deleted == False)  # noqa: E712
    )
    photo = photo_result.scalar_one_or_none()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    # Admin bypass: valid admin JWT grants access to all photos
    if admin_token:
        try:
            payload = jwt.decode(admin_token, settings.jwt_secret, algorithms=["HS256"])
            if payload.get("sub") == "admin":
                file_path = os.path.join(settings.photos_dir, str(photo.filename))
                if not os.path.exists(file_path):
                    raise HTTPException(status_code=404, detail="Photo file not found")
                return FileResponse(file_path, media_type=photo.content_type)
        except JWTError:
            pass
        raise HTTPException(status_code=403, detail="Invalid admin token")

    # Results phase: public access (contest is over)
    if phase == "finished":
        file_path = os.path.join(settings.photos_dir, str(photo.filename))
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Photo file not found")
        return FileResponse(file_path, media_type=photo.content_type)

    # Upload phase: no access yet
    if phase == "upload":
        raise HTTPException(status_code=404, detail="Photo not available yet")

    # Voting phase: require a known user_id, block own photo
    raw_uid = x_user_id or user_id
    if not raw_uid:
        raise HTTPException(status_code=401, detail="User ID required")
    try:
        user_uuid = uuid.UUID(raw_uid)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID")

    result = await db.execute(select(User).where(User.id == user_uuid))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Unknown user")

    if photo.user_id == user_uuid:
        raise HTTPException(status_code=403, detail="Cannot view your own photo")

    file_path = os.path.join(settings.photos_dir, str(photo.filename))
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Photo file not found")

    return FileResponse(file_path, media_type=photo.content_type)
