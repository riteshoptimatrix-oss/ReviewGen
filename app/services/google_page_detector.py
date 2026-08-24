from bs4 import BeautifulSoup
from typing import Optional
from app.core.logging import logger

class GooglePageDetector:
    
    PAGE_TYPE_MAPS_BUSINESS = "GOOGLE_MAPS_BUSINESS"
    PAGE_TYPE_REVIEW_PAGE = "GOOGLE_REVIEW_PAGE"
    PAGE_TYPE_SEARCH = "GOOGLE_SEARCH"
    PAGE_TYPE_CONSENT = "GOOGLE_CONSENT"
    PAGE_TYPE_CHALLENGE = "GOOGLE_CHALLENGE"
    PAGE_TYPE_ERROR = "GOOGLE_ERROR"
    PAGE_TYPE_UNKNOWN = "UNKNOWN"

    @classmethod
    def detect(cls, final_url: str, status_code: int, html: str, soup: BeautifulSoup) -> str:
        """
        Detects the type of Google page returned based on multiple signals.
        """
        if status_code == 404:
            return cls.PAGE_TYPE_ERROR

        # 1. Check for Consent
        if "consent.google.com" in final_url:
            return cls.PAGE_TYPE_CONSENT
            
        action_form = soup.find("form", action=lambda x: x and "consent.google.com" in x)
        if action_form:
            return cls.PAGE_TYPE_CONSENT

        # 2. Check for Challenge (Captcha/Sorry)
        title = soup.title.string if soup.title else ""
        challenge_signals = [
            "google.com/sorry/index" in html,
            "Captcha" in html,
            "unusual traffic" in html.lower(),
            "detected unusual traffic" in html.lower(),
            title and "sorry" in title.lower(),
        ]
        if any(challenge_signals):
            return cls.PAGE_TYPE_CHALLENGE

        # 3. Check for Maps Business
        if "maps.google.com/maps/place" in final_url or "google.com/maps/place" in final_url:
            return cls.PAGE_TYPE_MAPS_BUSINESS
            
        # Fallback signals for maps
        meta_og_url = soup.find("meta", property="og:url")
        if meta_og_url and isinstance(meta_og_url, dict) and "maps" in meta_og_url.get("content", ""): # BS4 Tag acts like dict for attrs
            pass
        if meta_og_url and meta_og_url.get("content") and "maps" in meta_og_url.get("content"):
             return cls.PAGE_TYPE_MAPS_BUSINESS

        # 4. Search Page
        if "/search?" in final_url:
            return cls.PAGE_TYPE_SEARCH

        # Review page if shortlink didn't resolve to full map but stayed as review somehow
        if "/review" in final_url:
             return cls.PAGE_TYPE_REVIEW_PAGE

        return cls.PAGE_TYPE_UNKNOWN
