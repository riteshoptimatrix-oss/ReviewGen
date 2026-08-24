class BusinessResolverError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(self.message)

class InvalidURLError(BusinessResolverError):
    def __init__(self, message: str = "The provided URL is invalid or malformed."):
        super().__init__("INVALID_URL", message)

class DomainNotAllowedError(BusinessResolverError):
    def __init__(self, message: str = "The provided domain is not allowed."):
        super().__init__("DOMAIN_NOT_ALLOWED", message)

class HttpTimeoutError(BusinessResolverError):
    def __init__(self, message: str = "The HTTP request timed out."):
        super().__init__("HTTP_TIMEOUT", message)

class HttpError(BusinessResolverError):
    def __init__(self, message: str = "An HTTP error occurred."):
        super().__init__("HTTP_ERROR", message)

class RedirectError(BusinessResolverError):
    def __init__(self, message: str = "Too many redirects or invalid redirect."):
        super().__init__("REDIRECT_ERROR", message)

class GoogleConsentError(BusinessResolverError):
    def __init__(self, message: str = "Google Consent page detected."):
        super().__init__("GOOGLE_CONSENT", message)

class GoogleChallengeError(BusinessResolverError):
    def __init__(self, message: str = "Google Challenge (Captcha) detected."):
        super().__init__("GOOGLE_CHALLENGE", message)

class GoogleNotFoundError(BusinessResolverError):
    def __init__(self, message: str = "Google page returned 404 Not Found."):
        super().__init__("GOOGLE_NOT_FOUND", message)

class UnsupportedPageError(BusinessResolverError):
    def __init__(self, message: str = "The page type is not supported for extraction."):
        super().__init__("UNSUPPORTED_PAGE", message)

class ExtractionFailedError(BusinessResolverError):
    def __init__(self, message: str = "Data extraction failed."):
        super().__init__("EXTRACTION_FAILED", message)

class UnknownError(BusinessResolverError):
    def __init__(self, message: str = "An unknown error occurred."):
        super().__init__("UNKNOWN_ERROR", message)
