import uuid
from datetime import datetime

from pydantic import BaseModel


class UploadResponse(BaseModel):
    user_id: uuid.UUID
    photo_id: uuid.UUID


class StatusResponse(BaseModel):
    phase: str


class VotingQueueResponse(BaseModel):
    queue: list[uuid.UUID]
    remaining: int


class VoteRequest(BaseModel):
    photo_id: uuid.UUID
    liked: bool


class VoteResponse(BaseModel):
    ok: bool
    remaining: int


class PhotoAdminItem(BaseModel):
    photo_id: uuid.UUID
    user_id: uuid.UUID
    uploaded_at: datetime
    file_size_kb: int | None
    like_count: int
    skip_count: int


class AdminPhotosResponse(BaseModel):
    photos: list[PhotoAdminItem]


class AdminSessionRequest(BaseModel):
    password: str


class AdminSessionResponse(BaseModel):
    token: str


class RankingItem(BaseModel):
    rank: int
    photo_id: uuid.UUID
    like_count: int
    skip_count: int


class ResultsResponse(BaseModel):
    rankings: list[RankingItem]
