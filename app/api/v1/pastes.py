from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.redis_client import RedisClient, get_redis
from app.schemas.paste import PasteCreate, PasteListResponse, PasteResponse
from app.services import paste as paste_service

router = APIRouter(prefix="/pastes", tags=["pastes"])


@router.post("/", response_model=PasteResponse, status_code=201)
async def create_paste(paste_data: PasteCreate, db: AsyncSession = Depends(get_db)):
    """Create a new paste (anonymous or authenticated)"""
    paste = await paste_service.create_paste(db, paste_data)
    return paste


@router.get("/{short_code}", response_model=PasteResponse)
async def get_paste(
    short_code: str, db: AsyncSession = Depends(get_db), redis: RedisClient = Depends(get_redis)
):
    """Get paste by short code"""
    paste = await paste_service.get_paste_by_short_code(db, short_code, redis)

    if not paste:
        raise HTTPException(status_code=404, detail="Paste not found")

    return paste


@router.get("/", response_model=List[PasteListResponse])
async def list_recent_pastes(limit: int = 20, db: AsyncSession = Depends(get_db)):
    """List recent public pastes"""
    pastes = await paste_service.list_recent_pastes(db, limit)
    return pastes
