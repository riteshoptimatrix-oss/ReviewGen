"""
Tests for the /api/v1/business/category endpoint.
Covers: valid calls, invalid URLs, SSRF attempts, missing categories, and fallback behavior.
No live network requests are made — all Google HTTP calls and DB calls are mocked.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock

from app.main import app
from app.db.session import get_db


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_cache_record(**kwargs) -> MagicMock:
    """Create a MagicMock that behaves like a MongoDB cache document object."""
    defaults = dict(
        input_url="https://g.page/r/test/review",
        final_url="https://www.google.com/maps/place/test",
        business_name=None,
        raw_category=None,
        normalized_category=None,
        category_confidence=0.0,
        category_source=None,
        address=None,
        phone=None,
        website=None,
        rating=None,
        review_count=None,
        status="SUCCESS",
    )
    defaults.update(kwargs)
    record = MagicMock(spec_set=list(defaults.keys()))
    for key, val in defaults.items():
        setattr(record, key, val)
    return record


def _make_resolver_result(html: str, final_url: str = "https://www.google.com/maps/place/test") -> MagicMock:
    result = MagicMock()
    result.html = html
    result.final_url = final_url
    result.status_code = 200
    result.duration_ms = 42
    return result


# ---------------------------------------------------------------------------
# DB override: replace the get_db FastAPI dependency with a no-op async generator
# that yields a plain MagicMock.  This avoids needing a live MongoDB connection.
# ---------------------------------------------------------------------------

async def _mock_db_dep():
    yield MagicMock()


@pytest.fixture(autouse=True)
def override_db():
    app.dependency_overrides[get_db] = _mock_db_dep
    yield
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


# ---------------------------------------------------------------------------
# Auth — API_KEY not set in test settings, so requests pass through.
# ---------------------------------------------------------------------------

class TestCategoryEndpointAuth:
    def test_missing_api_key_when_not_configured_passes(self, client):
        """When API_KEY is not set, requests without a key are not rejected with 401."""
        from app.core.exceptions import BusinessResolverError
        with patch(
            "app.repositories.business_repository.BusinessRepository.get_valid_cache_by_normalized_url",
            new_callable=AsyncMock,
            return_value=None,
        ):
            with patch(
                "app.services.google_resolver.GoogleResolver.resolve",
                new_callable=AsyncMock,
                side_effect=BusinessResolverError("HTTP_ERROR", "mocked failure"),
            ):
                with patch(
                    "app.repositories.business_repository.BusinessRepository.upsert_business_cache",
                    new_callable=AsyncMock,
                    return_value=_make_cache_record(),
                ):
                    resp = client.post(
                        "/api/v1/business/category",
                        json={"url": "https://g.page/r/abc/review"},
                    )
        # The request is processed and returns a proper JSON response — not 401
        assert resp.status_code == 200
        assert resp.json()["success"] is False
        assert resp.json()["error"]["code"] == "HTTP_ERROR"

    def test_invalid_url_returns_error_not_500(self, client):
        resp = client.post("/api/v1/business/category", json={"url": "not-a-url"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is False
        assert body["error"]["code"] in ("INVALID_URL", "DOMAIN_NOT_ALLOWED")


# ---------------------------------------------------------------------------
# Input validation & SSRF
# ---------------------------------------------------------------------------

class TestInputValidation:
    def test_empty_url_returns_error(self, client):
        resp = client.post("/api/v1/business/category", json={"url": ""})
        assert resp.status_code == 200
        assert resp.json()["success"] is False

    def test_url_too_long_returns_error(self, client):
        resp = client.post("/api/v1/business/category", json={"url": "https://g.page/r/" + "a" * 3000})
        assert resp.status_code == 200
        assert resp.json()["success"] is False

    def test_ssrf_localhost_rejected(self, client):
        resp = client.post("/api/v1/business/category", json={"url": "http://localhost/admin"})
        body = resp.json()
        assert body["success"] is False
        assert body["error"]["code"] == "DOMAIN_NOT_ALLOWED"

    def test_ssrf_internal_ip_rejected(self, client):
        resp = client.post("/api/v1/business/category", json={"url": "http://192.168.1.1/secret"})
        body = resp.json()
        assert body["success"] is False
        assert body["error"]["code"] == "DOMAIN_NOT_ALLOWED"

    def test_ssrf_file_scheme_rejected(self, client):
        resp = client.post("/api/v1/business/category", json={"url": "file:///etc/passwd"})
        assert resp.json()["success"] is False

    def test_g_page_domain_passes_validation(self, client):
        """g.page URLs pass URL validation — may fail later at HTTP stage."""
        from app.core.exceptions import BusinessResolverError
        with patch("app.repositories.business_repository.BusinessRepository.get_valid_cache_by_normalized_url", new_callable=AsyncMock, return_value=None):
            with patch("app.services.google_resolver.GoogleResolver.resolve", new_callable=AsyncMock,
                       side_effect=BusinessResolverError("HTTP_TIMEOUT", "Timed out")):
                with patch("app.repositories.business_repository.BusinessRepository.upsert_business_cache", new_callable=AsyncMock, return_value=MagicMock()):
                    resp = client.post("/api/v1/business/category", json={"url": "https://g.page/r/CdsN6Zff3D7IEBM/review"})
        body = resp.json()
        assert body["success"] is False
        assert body["error"]["code"] == "HTTP_TIMEOUT"   # NOT DOMAIN_NOT_ALLOWED

    def test_maps_google_com_passes_validation(self, client):
        from app.core.exceptions import BusinessResolverError
        with patch("app.repositories.business_repository.BusinessRepository.get_valid_cache_by_normalized_url", new_callable=AsyncMock, return_value=None):
            with patch("app.services.google_resolver.GoogleResolver.resolve", new_callable=AsyncMock,
                       side_effect=BusinessResolverError("HTTP_TIMEOUT", "Timed out")):
                with patch("app.repositories.business_repository.BusinessRepository.upsert_business_cache", new_callable=AsyncMock, return_value=MagicMock()):
                    resp = client.post("/api/v1/business/category", json={"url": "https://maps.google.com/maps/place/something"})
        body = resp.json()
        assert body["error"]["code"] != "DOMAIN_NOT_ALLOWED"


# ---------------------------------------------------------------------------
# Mocked extraction scenarios
# ---------------------------------------------------------------------------

class TestCategoryExtractionMocked:

    def test_successful_extraction_returns_normalized_category(self, client):
        mock_result = _make_resolver_result(
            "<html><body><span class='YhemCb'>Software company</span></body></html>"
        )
        cached_record = _make_cache_record(
            business_name="ABC Tech",
            raw_category="Software company",
            normalized_category="Software Company",
            category_confidence=0.95,
            category_source="google_category",
        )
        with patch("app.repositories.business_repository.BusinessRepository.get_valid_cache_by_normalized_url", new_callable=AsyncMock, return_value=None):
            with patch("app.services.google_resolver.GoogleResolver.resolve", new_callable=AsyncMock, return_value=mock_result):
                with patch("app.repositories.business_repository.BusinessRepository.upsert_business_cache", new_callable=AsyncMock, return_value=cached_record):
                    resp = client.post("/api/v1/business/category", json={"url": "https://g.page/r/test/review"})

        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["data"]["normalized_category"] == "Software Company"
        assert body["data"]["raw_category"] == "Software company"
        assert body["data"]["category_confidence"] >= 0.8
        assert body["error"] is None

    def test_google_challenge_returns_error_not_category(self, client):
        """A Google challenge page must NOT yield a category — it must return success=false."""
        html = "<html><body>Our systems have detected unusual traffic from your computer network.</body></html>"
        mock_result = _make_resolver_result(html)
        with patch("app.repositories.business_repository.BusinessRepository.get_valid_cache_by_normalized_url", new_callable=AsyncMock, return_value=None):
            with patch("app.services.google_resolver.GoogleResolver.resolve", new_callable=AsyncMock, return_value=mock_result):
                # The orchestrator calls upsert to cache the failure — return a minimal mock
                with patch("app.repositories.business_repository.BusinessRepository.upsert_business_cache", new_callable=AsyncMock, return_value=_make_cache_record()):
                    resp = client.post("/api/v1/business/category", json={"url": "https://g.page/r/test/review"})

        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is False
        assert body["data"] is None

    def test_missing_category_returns_null_normalized(self, client):
        """Valid page but no extractable category → normalized_category is null, success=True."""
        html = "<html><head><title>My Business</title></head><body><p>No category info here.</p></body></html>"
        mock_result = _make_resolver_result(html)
        cached_record = _make_cache_record(
            business_name="My Business",
            raw_category=None,
            normalized_category=None,
        )
        with patch("app.repositories.business_repository.BusinessRepository.get_valid_cache_by_normalized_url", new_callable=AsyncMock, return_value=None):
            with patch("app.services.google_resolver.GoogleResolver.resolve", new_callable=AsyncMock, return_value=mock_result):
                with patch("app.repositories.business_repository.BusinessRepository.upsert_business_cache", new_callable=AsyncMock, return_value=cached_record):
                    resp = client.post("/api/v1/business/category", json={"url": "https://g.page/r/test/review"})

        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["data"]["normalized_category"] is None

    def test_cached_result_skips_google_resolver(self, client):
        """Cache hit must bypass GoogleResolver entirely."""
        cached_record = _make_cache_record(
            input_url="https://g.page/r/cached/review",
            final_url="https://www.google.com/maps/place/cached",
            business_name="Cached Business",
            raw_category="Restaurant",
            normalized_category="Restaurant",
            category_confidence=0.95,
            category_source="google_category",
            status="SUCCESS",
        )
        with patch("app.repositories.business_repository.BusinessRepository.get_valid_cache_by_normalized_url", new_callable=AsyncMock, return_value=cached_record):
            with patch("app.services.google_resolver.GoogleResolver.resolve", new_callable=AsyncMock) as mock_resolve:
                resp = client.post("/api/v1/business/category", json={"url": "https://g.page/r/cached/review"})
                mock_resolve.assert_not_awaited()

        body = resp.json()
        assert body["success"] is True
        assert body["data"]["normalized_category"] == "Restaurant"

    def test_resolver_timeout_returns_error(self, client):
        """A timeout from GoogleResolver must produce success=false with HTTP_TIMEOUT code."""
        from app.core.exceptions import BusinessResolverError
        with patch("app.repositories.business_repository.BusinessRepository.get_valid_cache_by_normalized_url", new_callable=AsyncMock, return_value=None):
            with patch("app.services.google_resolver.GoogleResolver.resolve", new_callable=AsyncMock,
                       side_effect=BusinessResolverError("HTTP_TIMEOUT", "Request timed out")):
                with patch("app.repositories.business_repository.BusinessRepository.upsert_business_cache", new_callable=AsyncMock, return_value=_make_cache_record()):
                    resp = client.post("/api/v1/business/category", json={"url": "https://g.page/r/test/review"})

        body = resp.json()
        assert body["success"] is False
        assert body["error"]["code"] == "HTTP_TIMEOUT"


# ---------------------------------------------------------------------------
# Category normalizer unit tests
# ---------------------------------------------------------------------------

class TestCategoryNormalization:
    def test_software_company_normalizes(self):
        from app.services.category_normalizer import CategoryNormalizer
        result = CategoryNormalizer.normalize("software company")
        assert result.value == "Software Company"
        assert result.confidence >= 0.9

    def test_restaurant_normalizes(self):
        from app.services.category_normalizer import CategoryNormalizer
        result = CategoryNormalizer.normalize("Indian restaurant")
        assert result.value == "Restaurant"

    def test_cafe_normalizes(self):
        from app.services.category_normalizer import CategoryNormalizer
        result = CategoryNormalizer.normalize("coffee shop")
        assert result.value == "Cafe"

    def test_clothing_store_normalizes(self):
        from app.services.category_normalizer import CategoryNormalizer
        result = CategoryNormalizer.normalize("Clothing store")
        assert result.value == "Clothing Store"

    def test_dentist_normalizes(self):
        from app.services.category_normalizer import CategoryNormalizer
        result = CategoryNormalizer.normalize("dental clinic")
        assert result.value == "Dentist"

    def test_unknown_category_returns_none(self):
        from app.services.category_normalizer import CategoryNormalizer
        result = CategoryNormalizer.normalize("xyz qwerty unknown 12345")
        assert result.value is None
        assert result.confidence == 0.0

    def test_empty_string_returns_none(self):
        from app.services.category_normalizer import CategoryNormalizer
        result = CategoryNormalizer.normalize("")
        assert result.value is None

    def test_none_input_returns_none(self):
        from app.services.category_normalizer import CategoryNormalizer
        result = CategoryNormalizer.normalize(None)
        assert result.value is None

    def test_case_insensitive_match(self):
        from app.services.category_normalizer import CategoryNormalizer
        result = CategoryNormalizer.normalize("CAFE")
        assert result.value == "Cafe"

    def test_partial_match_confidence_lower(self):
        from app.services.category_normalizer import CategoryNormalizer
        result = CategoryNormalizer.normalize("Best Italian Restaurant in Town")
        assert result.value == "Restaurant"
        assert result.confidence < 1.0
