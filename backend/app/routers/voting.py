import random
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import require_voter
from app.models import ContestState, Photo, Vote
from app.schemas import VoteRequest, VoteResponse, VotingQueueResponse
from app.ws_manager import manager

router = APIRouter()


async def _get_phase(db: AsyncSession) -> str:
    result = await db.execute(select(ContestState).where(ContestState.id == 1))
    state = result.scalar_one_or_none()
    return state.phase if state else "upload"


@router.get("/api/voting/queue", response_model=VotingQueueResponse)
async def get_voting_queue(
    voter_id: uuid.UUID = Depends(require_voter),
    db: AsyncSession = Depends(get_db),
):
    if await _get_phase(db) != "voting":
        raise HTTPException(status_code=409, detail="Contest is not in voting phase")

    already_voted = select(Vote.photo_id).where(Vote.voter_id == voter_id)
    result = await db.execute(
        select(Photo.id).where(
            Photo.user_id != voter_id,
            Photo.is_deleted == False,  # noqa: E712
            Photo.id.notin_(already_voted),
        )
    )
    photo_ids = [row[0] for row in result.all()]
    random.shuffle(photo_ids)
    return VotingQueueResponse(queue=photo_ids, remaining=len(photo_ids))


@router.post("/api/vote", response_model=VoteResponse)
async def cast_vote(
    body: VoteRequest,
    voter_id: uuid.UUID = Depends(require_voter),
    db: AsyncSession = Depends(get_db),
):
    if await _get_phase(db) != "voting":
        raise HTTPException(status_code=403, detail="Voting is not active")

    photo_result = await db.execute(
        select(Photo).where(Photo.id == body.photo_id, Photo.is_deleted == False)  # noqa: E712
    )
    photo = photo_result.scalar_one_or_none()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")
    if photo.user_id == voter_id:
        raise HTTPException(status_code=403, detail="Cannot vote on your own photo")

    existing = await db.execute(
        select(Vote).where(Vote.voter_id == voter_id, Vote.photo_id == body.photo_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Already voted on this photo")

    db.add(Vote(voter_id=voter_id, photo_id=body.photo_id, liked=body.liked))
    await db.commit()

    already_voted = select(func.count()).select_from(Vote).where(Vote.voter_id == voter_id)
    total_photos = select(func.count()).select_from(Photo).where(
        Photo.user_id != voter_id,
        Photo.is_deleted == False,  # noqa: E712
    )
    voted_count = (await db.execute(already_voted)).scalar()
    total_count = (await db.execute(total_photos)).scalar()
    remaining = max(0, total_count - voted_count)

    like_count = await db.scalar(
        select(func.count()).select_from(Vote).where(
            Vote.photo_id == body.photo_id, Vote.liked == True  # noqa: E712
        )
    )
    skip_count = await db.scalar(
        select(func.count()).select_from(Vote).where(
            Vote.photo_id == body.photo_id, Vote.liked == False  # noqa: E712
        )
    )
    await manager.broadcast_to_admins({
        "event": "vote_updated",
        "photo_id": str(body.photo_id),
        "like_count": like_count or 0,
        "skip_count": skip_count or 0,
    })

    return VoteResponse(ok=True, remaining=remaining)
