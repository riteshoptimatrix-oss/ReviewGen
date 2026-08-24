import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.business_cache import BusinessCache


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _url_hash(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


class BusinessRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_valid_cache_by_normalized_url(self, normalized_url: str) -> Optional[BusinessCache]:
        """
        Returns a cached record if it exists and hasn't expired.
        """
        result = await self.db.execute(
            select(BusinessCache).where(BusinessCache.url_hash == _url_hash(normalized_url))
        )
        record = result.scalar_one_or_none()

        if record and record.last_checked_at:
            expiry_time = record.last_checked_at + timedelta(hours=settings.cache_ttl_hours)
            if _utcnow() <= expiry_time:
                return record

        return None

    async def upsert_business_cache(self, data: dict) -> BusinessCache:
        """
        Creates or updates a cache record based on normalized_url.
        """
        normalized_url = data["normalized_url"]

        now = _utcnow()
        data["last_checked_at"] = now
        data["updated_at"] = now

        result = await self.db.execute(
            select(BusinessCache).where(BusinessCache.url_hash == _url_hash(normalized_url))
        )
        record = result.scalar_one_or_none()

        if record is None:
            data.setdefault("created_at", now)
            record = BusinessCache(url_hash=_url_hash(normalized_url), **data)
            self.db.add(record)
        else:
            for key, value in data.items():
                setattr(record, key, value)

        await self.db.commit()
        await self.db.refresh(record)
        return record
