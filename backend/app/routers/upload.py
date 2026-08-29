import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models import ContestState, Photo, User
from app.schemas import StatusResponse, UploadResponse

router = APIRouter()

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

MAGIC_BYTES: dict[bytes, str] = {
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG": "image/png",
    b"RIFF": "image/webp",
    b"GIF8": "image/gif",
}


def _validate_magic(data: bytes, content_type: str) -> bool:
    for magic, ct in MAGIC_BYTES.items():
        if data.startswith(magic):
            return ct == content_type
    return False


@router.get("/api/status", response_model=StatusResponse)
async def get_status(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ContestState).where(ContestState.id == 1))
    state = result.scalar_one_or_none()
    return {"phase": state.phase if state else "upload"}


@router.post("/api/upload", response_model=UploadResponse)
async def upload_photo(photo: UploadFile, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ContestState).where(ContestState.id == 1))
    state = result.scalar_one_or_none()
    if state and state.phase != "upload":
        raise HTTPException(status_code=409, detail="Upload is closed — contest is in progress")

    if photo.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, WebP, and GIF are allowed")

    data = await photo.read()
    if len(data) > MAX_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="File too large — max 10 MB")

    if not _validate_magic(data[:12], photo.content_type):
        raise HTTPException(status_code=400, detail="File content does not match declared type")

    user = User()
    db.add(user)
    await db.flush()

    filename_uuid = uuid.uuid4()
    file_path = os.path.join(settings.photos_dir, str(filename_uuid))
    os.makedirs(settings.photos_dir, exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(data)

    photo_row = Photo(
        user_id=user.id,
        filename=filename_uuid,
        content_type=photo.content_type,
        file_size_kb=len(data) // 1024,
    )
    db.add(photo_row)
    await db.commit()

    return UploadResponse(user_id=user.id, photo_id=photo_row.id)
