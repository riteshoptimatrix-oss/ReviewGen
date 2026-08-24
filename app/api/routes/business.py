from fastapi import APIRouter, Request, Depends
from typing import List

from app.schemas.business import ResolveRequest, ResolveResponse, BulkResolveRequest
from app.services.resolution_orchestrator import ResolutionOrchestrator
from app.services.bulk_processor import BulkProcessor
from app.db.session import get_db
from app.api.dependencies.auth import get_api_key
from app.api.dependencies.rate_limit import check_rate_limit

router = APIRouter(dependencies=[Depends(get_api_key), Depends(check_rate_limit)])

@router.post("/resolve", response_model=ResolveResponse)
async def resolve_business(request: ResolveRequest, req: Request, db = Depends(get_db)):
    """
    Resolves a Google Business Profile URL for basic data (Legacy Phase 1).
    Now delegates to orchestrator for caching and category.
    """
    client = req.app.state.http_client
    orchestrator = ResolutionOrchestrator(client, db)
    return await orchestrator.process_url(request.url)

@router.post("/category", response_model=ResolveResponse)
async def get_business_category(request: ResolveRequest, req: Request, db = Depends(get_db)):
    """
    Resolves category with caching and normalizer.
    """
    client = req.app.state.http_client
    orchestrator = ResolutionOrchestrator(client, db)
    return await orchestrator.process_url(request.url)

@router.post("/category/bulk", response_model=List[ResolveResponse])
async def get_business_category_bulk(request: BulkResolveRequest, req: Request, db = Depends(get_db)):
    """
    Resolves multiple URLs with bounded concurrency.
    """
    client = req.app.state.http_client
    processor = BulkProcessor(client)
    return await processor.process_batch(request.urls, db)
