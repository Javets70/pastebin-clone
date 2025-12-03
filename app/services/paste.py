import json
import secrets
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis_client import RedisClient
from app.models.paste import Paste
from app.schemas.paste import PasteCreate


def generate_short_code(length: int = 8) -> str:
    """Generate random short code for paste URL"""
    return secrets.token_urlsafe(length)[:length]


async def create_paste(db: AsyncSession, paste_data: PasteCreate) -> Paste:
    # Generate unique short code
    short_code = generate_short_code()

    # Calculate expiration
    expires_at = None
    if paste_data.expires_in_hours:
        expires_at = datetime.utcnow() + timedelta(hours=paste_data.expires_in_hours)

    paste = Paste(
        title=paste_data.title,
        content=paste_data.content,
        language=paste_data.language,
        short_code=short_code,
        is_public=paste_data.is_public,
        expires_at=expires_at,
    )

    db.add(paste)
    await db.commit()
    await db.refresh(paste)
    return paste


async def get_paste_by_short_code(
    db: AsyncSession, short_code: str, redis: RedisClient
) -> Optional[Paste]:
    cached = await redis.get(short_code)
    if cached:
        paste_dict = json.loads(cached)
        # Increment view count in background (don't wait)
        result = await db.execute(select(Paste).where(Paste.short_code == short_code))
        paste = result.scalar_one_or_none()
        if paste:
            paste.view_count += 1
            await db.commit()
        return Paste(**paste_dict)

    result = await db.execute(select(Paste).where(Paste.short_code == short_code))
    paste = result.scalar_one_or_none()

    if paste:
        # Increment view count
        paste.view_count += 1
        await db.commit()
        await db.refresh(paste)
        # Cache for 5 minutes
        paste_dict = {
            "id": paste.id,
            "title": paste.title,
            "content": paste.content,
            "language": paste.language,
            "short_code": paste.short_code,
            "is_public": paste.is_public,
            "view_count": paste.view_count,
            "created_at": paste.created_at.isoformat(),
        }
        await redis.set(short_code, json.dumps(paste_dict), expire=300)

    return paste


async def list_recent_pastes(db: AsyncSession, limit: int = 20) -> list[Paste]:
    result = await db.execute(
        select(Paste).where(Paste.is_public == True).order_by(Paste.created_at.desc()).limit(limit)
    )
    return list(result.scalars().all())
