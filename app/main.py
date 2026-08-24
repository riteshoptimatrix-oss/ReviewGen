from fastapi import FastAPI
from contextlib import asynccontextmanager
import httpx

from app.api.routes import health, business
from app.core.config import settings
from app.core.logging import logger, setup_logging
from app.db.session import init_db, close_db

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup global HTTP client
    limits = httpx.Limits(max_keepalive_connections=50, max_connections=100)
    timeout = httpx.Timeout(settings.http_timeout_seconds)
    client = httpx.AsyncClient(
        limits=limits,
        timeout=timeout,
        follow_redirects=True,
        max_redirects=settings.max_redirects,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5"
        }
    )
    app.state.http_client = client

    try:
        await init_db()
    except Exception as exc:
        logger.warning(f"MongoDB initialization skipped/failed: {exc}")

    yield

    await client.aclose()
    await close_db()

app = FastAPI(
    title="Google Business Profile Resolver",
    description="Resolves Google Business URLs and extracts structured data",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(health.router, tags=["health"])
app.include_router(business.router, prefix="/api/v1/business", tags=["business"])
