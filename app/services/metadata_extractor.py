from bs4 import BeautifulSoup
from typing import Dict, Any
from app.utils.text_utils import clean_text

class MetadataExtractor:
    
    @classmethod
    def extract(cls, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Extracts information from Meta tags (OpenGraph, standard meta).
        """
        extracted = {}
        
        # Title (often contains business name)
        og_title = soup.find("meta", property="og:title")
        title = og_title.get("content") if og_title else None
        
        if not title and soup.title:
            title = soup.title.string
            
        if title:
            title = clean_text(title)
            # Google Maps titles are often "Business Name - Google Maps"
            if title and " - Google Maps" in title:
                title = title.replace(" - Google Maps", "")
            
            # Prevent generic names from being used as the business name
            generic_titles = {"Google", "Google Maps", "Google Search", "Sign in - Google Accounts"}
            if title not in generic_titles:
                extracted["business_name"] = title
            
        # URL (can sometimes be the website or the google page)
        # We avoid returning google maps url as the business website.
        
        return extracted
