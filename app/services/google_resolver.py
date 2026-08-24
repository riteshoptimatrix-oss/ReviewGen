import time
import httpx
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.core.exceptions import (
    HttpTimeoutError,
    HttpError,
    RedirectError
)
from app.core.logging import logger
from app.core.config import settings

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.core.config import settings

class ResolverResult(BaseModel):
    input_url: str
    final_url: str
    status_code: int
    content_type: str
    html: str
    redirect_chain: List[str]
    duration_ms: int

class GoogleResolver:
    def __init__(self, client: httpx.AsyncClient):
        self.client = client

    @retry(
        stop=stop_after_attempt(settings.retry_attempts),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((HttpTimeoutError, HttpError)),
        reraise=True
    )
    async def resolve(self, url: str) -> ResolverResult:
        start_time = time.time()
        logger.info(f"Resolving URL: {url}")
        
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
            }
            # We must use follow_redirects=True manually or via client.
            # httpx.AsyncClient follow_redirects is configured in lifespan.
            response = await self.client.get(url, headers=headers)
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            redirect_chain = [str(req.url) for req in response.history]
            final_url = str(response.url)
            status_code = response.status_code
            content_type = response.headers.get("content-type", "")
            
            # Google often returns 200 for maps pages, but sometimes 404 for removed businesses.
            # We don't raise immediately on 404, we let the detector handle it.
            
            return ResolverResult(
                input_url=url,
                final_url=final_url,
                status_code=status_code,
                content_type=content_type,
                html=response.text,
                redirect_chain=redirect_chain,
                duration_ms=duration_ms
            )
            
        except httpx.TimeoutException as e:
            logger.error(f"Timeout resolving {url}: {str(e)}")
            raise HttpTimeoutError()
        except httpx.TooManyRedirects as e:
            logger.error(f"Too many redirects for {url}: {str(e)}")
            raise RedirectError("Too many redirects.")
        except httpx.RequestError as e:
            logger.error(f"HTTP request error for {url}: {str(e)}")
            raise HttpError(f"HTTP error: {str(e)}")
