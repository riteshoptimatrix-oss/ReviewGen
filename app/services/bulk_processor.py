import asyncio
import httpx
from typing import List

from app.schemas.business import ErrorDetail, ResolveResponse
from app.services.resolution_orchestrator import ResolutionOrchestrator
from app.core.config import settings

class BulkProcessor:
    def __init__(self, http_client: httpx.AsyncClient):
        self.http_client = http_client
        self.semaphore = asyncio.Semaphore(settings.max_concurrent_requests)

    async def process_batch(self, urls: List[str], db_session) -> List[ResolveResponse]:
        """
        Processes a batch of URLs with bounded concurrency.
        Each concurrent task gets its own AsyncSession because a single
        SQLAlchemy AsyncSession is not safe for parallel use.
        """
        async def sem_process(url: str):
            async with self.semaphore:
                session = db_session
                if session is None:
                    from app.db.session import db
                    session = db
                orchestrator = ResolutionOrchestrator(self.http_client, session)
                return await orchestrator.process_url(url)

        tasks = [sem_process(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        final_results = []
        for i, res in enumerate(results):
            if isinstance(res, Exception):
                final_results.append(ResolveResponse(
                    success=False,
                    error=ErrorDetail(code="UNKNOWN_ERROR", message="An unknown error occurred.")
                ))
            else:
                final_results.append(res)

        return final_results
