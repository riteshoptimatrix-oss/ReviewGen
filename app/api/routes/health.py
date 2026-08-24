from fastapi import APIRouter, Depends
from sqlalchemy import text

from app.db.session import get_db

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "ok"}

@router.get("/health/db")
async def db_health_check(db = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ok", "db": "connected"}
    except Exception as e:
        return {"status": "error", "db": str(e)}

@router.get("/metrics")
async def get_metrics():
    # Placeholder for Prometheus metrics or internal stats
    return {"status": "not_implemented_yet"}
