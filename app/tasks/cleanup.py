from datetime import datetime

from app.db.session import AsyncSessionLocal
from sqlalchemy import delete, select

from app.core.celery_app import celery_app
from app.models.paste import Paste


@celery_app.task(name="cleanup_expired_pastes")
def cleanup_expired_pastes():
    """Delete expired pastes (runs periodically)"""
    import asyncio

    async def _cleanup():
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Paste).where(Paste.expires_at != None, Paste.expires_at < datetime.utcnow())
            )
            expired_pastes = result.scalars().all()

            for paste in expired_pastes:
                await db.delete(paste)

            await db.commit()
            return len(expired_pastes)

    deleted_count = asyncio.run(_cleanup())
    return f"Deleted {deleted_count} expired pastes"


@celery_app.task(name="send_email_notification")
def send_email_notification(email: str, subject: str, body: str):
    """Send email notification (example task)"""
    # Implement email sending logic here
    import time

    time.sleep(2)  # Simulate email sending
    return f"Email sent to {email}"
