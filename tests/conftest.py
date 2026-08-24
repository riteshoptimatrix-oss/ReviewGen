import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, AsyncMock
from app.main import app
from app.db.session import get_db


async def _mock_db_dep():
    """Yield a plain MagicMock so no live MongoDB is needed during tests."""
    yield MagicMock()


@pytest.fixture
def client():
    # Override the DB dependency globally for all requests
    app.dependency_overrides[get_db] = _mock_db_dep
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.pop(get_db, None)
