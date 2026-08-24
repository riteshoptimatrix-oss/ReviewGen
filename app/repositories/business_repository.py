import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional
from types import SimpleNamespace

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import settings


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _url_hash(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


class CacheRecord(SimpleNamespace):
    pass


class BusinessRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = self.db.business_cache

    async def get_valid_cache_by_normalized_url(self, normalized_url: str) -> Optional[CacheRecord]:
        """
        Returns a cached record if it exists and hasn't expired.
        """
        record = await self.collection.find_one({"url_hash": _url_hash(normalized_url)})

        if record and record.get("last_checked_at"):
            expiry_time = record["last_checked_at"] + timedelta(hours=settings.cache_ttl_hours)
            if _utcnow() <= expiry_time:
                # Provide defaults for missing fields to mimic SQLAlchemy model
                for key in ["final_url", "business_name", "raw_category", "normalized_category", 
                            "category_confidence", "category_source", "address", "phone", 
                            "website", "rating", "review_count", "error_code"]:
                    record.setdefault(key, None)
                record.setdefault("status", "SUCCESS")
                return CacheRecord(**record)

        return None

    async def upsert_business_cache(self, data: dict) -> CacheRecord:
        """
        Creates or updates a cache record based on normalized_url.
        """
        normalized_url = data["normalized_url"]
        url_hash = _url_hash(normalized_url)

        now = _utcnow()
        data["last_checked_at"] = now
        data["updated_at"] = now

        update_data = {
            "$set": data,
            "$setOnInsert": {"created_at": now, "url_hash": url_hash}
        }

        # motor's find_one_and_update can return the document after update with ReturnDocument.AFTER
        # but PyMongo 4+ uses ReturnDocument, we can just use new=True or return_document=True
        # Actually in motor/pymongo it is return_document=ReturnDocument.AFTER
        from pymongo import ReturnDocument
        result = await self.collection.find_one_and_update(
            {"url_hash": url_hash},
            update_data,
            upsert=True,
            return_document=ReturnDocument.AFTER
        )
        
        # Provide defaults
        for key in ["final_url", "business_name", "raw_category", "normalized_category", 
                    "category_confidence", "category_source", "address", "phone", 
                    "website", "rating", "review_count", "error_code"]:
            result.setdefault(key, None)
        result.setdefault("status", "SUCCESS")

        return CacheRecord(**result)
