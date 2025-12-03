from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean

from app.core.database import Base


class Paste(Base):
    __tablename__ = "pastes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=True)
    content = Column(Text, nullable=False)
    language = Column(String(50), default="text")

    # URL shortcode (e.g., "abc123")
    short_code = Column(String(10), unique=True, index=True, nullable=False)

    # Privacy
    is_public = Column(Boolean, default=True)
    password_hash = Column(String(255), nullable=True)

    # Expiration
    expires_at = Column(DateTime, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    view_count = Column(Integer, default=0)

    # For future auth
    user_id = Column(Integer, nullable=True)
