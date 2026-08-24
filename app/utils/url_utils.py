import urllib.parse
from app.core.exceptions import InvalidURLError, DomainNotAllowedError

ALLOWED_DOMAINS = {
    "g.page",
    "www.google.com",
    "google.com",
    "maps.google.com"
}

def validate_google_url(url: str) -> str:
    """
    Validates the URL to prevent SSRF and ensure it is an allowed Google domain.
    Raises InvalidURLError or DomainNotAllowedError if invalid.
    """
    if not url or len(url) > 2048:
        raise InvalidURLError("URL is empty or too long.")
        
    try:
        parsed = urllib.parse.urlparse(url)
    except ValueError:
        raise InvalidURLError("Failed to parse URL.")
        
    # Strip /review or /review/ from the path
    path = parsed.path
    if path.endswith("/review"):
        path = path[:-7]
    elif path.endswith("/review/"):
        path = path[:-8]
        
    url = urllib.parse.urlunparse((parsed.scheme, parsed.netloc, path, parsed.params, parsed.query, parsed.fragment))
    
    if parsed.scheme not in ("http", "https"):
        raise InvalidURLError(f"Invalid scheme: {parsed.scheme}")
        
    hostname = parsed.hostname
    if not hostname:
        raise InvalidURLError("No hostname found in URL.")
        
    hostname = hostname.lower()
    
    if hostname not in ALLOWED_DOMAINS:
        raise DomainNotAllowedError(f"Domain '{hostname}' is not allowed.")
        
    return url
