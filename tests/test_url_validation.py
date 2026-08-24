import pytest
from app.utils.url_utils import validate_google_url
from app.core.exceptions import InvalidURLError, DomainNotAllowedError

def test_valid_urls():
    assert validate_google_url("https://g.page/r/abc/review") == "https://g.page/r/abc/review"
    assert validate_google_url("https://maps.google.com/maps?q=abc") == "https://maps.google.com/maps?q=abc"
    assert validate_google_url("http://www.google.com/maps/place/xyz") == "http://www.google.com/maps/place/xyz"

def test_invalid_urls():
    with pytest.raises(InvalidURLError):
        validate_google_url("not_a_url")
        
    with pytest.raises(InvalidURLError):
        validate_google_url("ftp://google.com")

def test_unallowed_domains():
    with pytest.raises(DomainNotAllowedError):
        validate_google_url("https://example.com/g.page")
        
    with pytest.raises(DomainNotAllowedError):
        validate_google_url("https://localhost:8000")
