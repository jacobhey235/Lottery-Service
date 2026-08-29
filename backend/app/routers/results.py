from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import Integer, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import ContestState, Photo, Vote
from app.schemas import RankingItem, ResultsResponse

router = APIRouter()


@router.get("/api/results", response_model=ResultsResponse)
async def get_results(db: AsyncSession = Depends(get_db)):
    state_result = await db.execute(select(ContestState).where(ContestState.id == 1))
    state = state_result.scalar_one_or_none()
    if not state or state.phase != "finished":
        raise HTTPException(status_code=409, detail="Contest is not finished yet")

    rows = await db.execute(
        select(
            Photo.id,
            func.sum(cast(Vote.liked, Integer)).label("like_count"),
            func.sum(cast(~Vote.liked, Integer)).label("skip_count"),
        )
        .join(Vote, Vote.photo_id == Photo.id, isouter=True)
        .where(Photo.is_deleted == False)  # noqa: E712
        .group_by(Photo.id)
        .order_by(func.sum(cast(Vote.liked, Integer)).desc().nullslast())
    )

    rankings = []
    for rank, row in enumerate(rows.all(), start=1):
        rankings.append(
            RankingItem(
                rank=rank,
                photo_id=row[0],
                like_count=int(row[1] or 0),
                skip_count=int(row[2] or 0),
            )
        )

    return ResultsResponse(rankings=rankings)
