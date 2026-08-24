import asyncio
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup
import httpx

from app.schemas.business import BusinessData, BusinessMeta, ResolveResponse
from app.services.google_resolver import GoogleResolver
from app.services.google_page_detector import GooglePageDetector
from app.services.business_extractor import BusinessExtractor
from app.services.category_normalizer import CategoryNormalizer
from app.repositories.business_repository import BusinessRepository
from app.utils.url_utils import validate_google_url
from app.core.exceptions import BusinessResolverError
from app.core.logging import logger

class ResolutionOrchestrator:
    # Single-flight locks for concurrent requests to the same URL
    _locks: Dict[str, asyncio.Lock] = {}

    def __init__(self, http_client: httpx.AsyncClient, db_session):
        self.http_client = http_client
        self.db_session = db_session
        self.repo = BusinessRepository(db_session)
        
    async def process_url(self, raw_url: str) -> ResolveResponse:
        try:
            validated_url = validate_google_url(raw_url)
        except BusinessResolverError as e:
            from app.schemas.business import ErrorDetail
            return ResolveResponse(success=False, error=ErrorDetail(code=e.code, message=e.message))
            
        # Single-flight lock acquisition
        if validated_url not in self._locks:
            self._locks[validated_url] = asyncio.Lock()
            
        async with self._locks[validated_url]:
            return await self._process_url_internal(validated_url)
            
    async def _process_url_internal(self, validated_url: str) -> ResolveResponse:
        from app.schemas.business import ErrorDetail
        # 1. Check cache by input URL first (fastest)
        cached = await self.repo.get_valid_cache_by_normalized_url(validated_url)
        if cached and cached.status == "SUCCESS":
            data = self._cache_to_business_data(cached)
            return ResolveResponse(success=True, data=data)
            
        # 2. Not cached, resolve via HTTP
        resolver = GoogleResolver(self.http_client)
        try:
            result = await resolver.resolve(validated_url)
        except BusinessResolverError as e:
            await self.repo.upsert_business_cache({
                "input_url": validated_url,
                "normalized_url": validated_url,
                "status": e.code,
                "error_code": e.code
            })
            return ResolveResponse(success=False, error=ErrorDetail(code=e.code, message=e.message))
            
        # 3. Detect page type
        soup = BeautifulSoup(result.html, "lxml")
        page_type = GooglePageDetector.detect(result.final_url, result.status_code, result.html, soup)
        
        meta = BusinessMeta(status_code=result.status_code, page_type=page_type, duration_ms=result.duration_ms)
        
        if page_type in [GooglePageDetector.PAGE_TYPE_CONSENT, GooglePageDetector.PAGE_TYPE_CHALLENGE, GooglePageDetector.PAGE_TYPE_ERROR, GooglePageDetector.PAGE_TYPE_UNKNOWN]:
            error_code = page_type.replace("GOOGLE_", "")
            error_msg = f"Google page type: {page_type}"
            if page_type == GooglePageDetector.PAGE_TYPE_UNKNOWN:
                error_code = "UNSUPPORTED_PAGE"
                error_msg = "The page type is not supported for extraction."
            if page_type == GooglePageDetector.PAGE_TYPE_ERROR:
                error_code = "GOOGLE_NOT_FOUND"
                error_msg = "Google page returned 404 Not Found."
                
            await self.repo.upsert_business_cache({
                "input_url": validated_url,
                "normalized_url": validated_url,
                "final_url": result.final_url,
                "status": error_code,
                "error_code": error_code
            })
            return ResolveResponse(success=False, error=ErrorDetail(code=error_code, message=error_msg))

        # 4. Extract data
        extracted = BusinessExtractor.extract(result.html, validated_url, result.final_url)
        
        # 5. Normalize category
        norm_result = CategoryNormalizer.normalize(extracted.raw_category)
        
        # 6. Save to cache
        cache_data = {
            "input_url": validated_url,
            "normalized_url": validated_url,
            "final_url": result.final_url,
            "business_name": extracted.business_name,
            "raw_category": extracted.raw_category,
            "normalized_category": norm_result.value,
            "category_confidence": norm_result.confidence,
            "category_source": norm_result.source,
            "address": extracted.address,
            "phone": extracted.phone,
            "website": extracted.website,
            "rating": extracted.rating,
            "review_count": extracted.review_count,
            "status": "SUCCESS"
        }
        
        cached_record = await self.repo.upsert_business_cache(cache_data)
        
        final_data = self._cache_to_business_data(cached_record)
        return ResolveResponse(success=True, data=final_data)
        
    def _cache_to_business_data(self, record) -> BusinessData:
        return BusinessData(
            input_url=record.input_url,
            final_url=record.final_url,
            business_name=record.business_name,
            raw_category=record.raw_category,
            normalized_category=record.normalized_category,
            category_confidence=record.category_confidence,
            category_source=record.category_source,
            address=record.address,
            phone=record.phone,
            website=record.website,
            rating=record.rating,
            review_count=record.review_count
        )
