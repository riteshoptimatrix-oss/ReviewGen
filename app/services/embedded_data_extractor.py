import re
import json
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional
from app.core.logging import logger
from app.utils.text_utils import clean_text

class EmbeddedDataExtractor:
    
    @classmethod
    def extract(cls, soup: BeautifulSoup, html: str) -> Dict[str, Any]:
        """
        Extracts information from Google's embedded JavaScript structures if available.
        This is a fallback and can be fragile, so we do it carefully.
        """
        extracted = {}
        
        # Example pattern: Google sometimes embeds state in window.APP_INITIALIZATION_STATE
        # We can look for specific json-like structures but we should be defensive.
        
        # Look for the business name in window.APP_INITIALIZATION_STATE or similar
        # For Phase 1, we will implement a basic regex for the business name if it's very clear.
        # Often, it's encoded in the initData.
        
        # Search for ["Business Name", ...
        # This is very specific and might change.
        # We won't rely on it too heavily.
        
        # Another source: <h1 class="fontHeadlineLarge">
        # Google maps usually has an h1 for the business name
        h1 = soup.find("h1")
        if h1 and h1.string:
            name = clean_text(h1.string)
            if name:
                extracted["business_name"] = name
                
        # Address: sometimes in button aria-labels
        address_btn = soup.find("button", {"data-item-id": "address"})
        if address_btn and address_btn.get("aria-label"):
            aria_label = address_btn.get("aria-label")
            if isinstance(aria_label, str) and aria_label.startswith("Address: "):
                extracted["address"] = clean_text(aria_label.replace("Address: ", ""))
                
        # Phone
        phone_btn = soup.find("button", {"data-item-id": lambda x: x and "phone:tel:" in x})
        if phone_btn and phone_btn.get("data-item-id"):
            item_id = phone_btn.get("data-item-id")
            if isinstance(item_id, str):
                phone = item_id.replace("phone:tel:", "")
                extracted["phone"] = clean_text(phone)
                
        # Website
        website_btn = soup.find("a", {"data-item-id": "authority"})
        if website_btn and website_btn.get("href"):
            extracted["website"] = clean_text(website_btn.get("href"))
            
        # Category: usually a button in a specific container, hard to pinpoint without exact classes
        # Let's try to find a button with a class that usually holds the category
        category_btn = soup.find("button", {"jsaction": "pane.rating.category"})
        if category_btn and category_btn.string:
            extracted["raw_category"] = clean_text(category_btn.string)

        return extracted
