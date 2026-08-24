from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class BusinessCache(Base):
    __tablename__ = "business_cache"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    url_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    input_url: Mapped[str] = mapped_column(Text)
    normalized_url: Mapped[str] = mapped_column(Text)
    final_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    business_name: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    raw_category: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    normalized_category: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    category_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    category_source: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    review_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(64), default="SUCCESS", index=True)
    error_code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    updated_at: Mapped[datetime] = mapped_column(DateTime)
    last_checked_at: Mapped[datetime] = mapped_column(DateTime)
