import re
from bs4 import BeautifulSoup
from typing import Dict, Any
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
            generic_titles = {"Google", "Google Maps", "Google Search", "Sign in - Google Accounts", "Sign in"}
            if name not in generic_titles:
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
            
        # Fallback using regex on HTML if category is not found (useful for search pages)
        if "raw_category" not in extracted or not extracted["raw_category"]:
            match1 = re.search(r'<span class="YhemCb"[^>]*>(.*?)</span>', html, re.IGNORECASE)
            if match1:
                scraped_text = re.sub(r'<[^>]+>', '', match1.group(1))
                extracted["raw_category"] = clean_text(scraped_text.split(' in ')[0])
            else:
                match2 = re.search(r'data-attrid="subtitle"[^>]*>.*?<span[^>]*>(.*?)</span>', html, re.IGNORECASE)
                if match2:
                    extracted["raw_category"] = clean_text(re.sub(r'<[^>]+>', '', match2.group(1)))

        # Final Brute-force Fallback for known categories
        if "raw_category" not in extracted or not extracted["raw_category"]:
            common_cats = [
                'tour operator', 'travel agency', 'software training institute', 'restaurant', 'cafe', 
                'coffee shop', 'plumber', 'electrician', 'hvac contractor', 'real estate agency', 
                'law firm', 'lawyer', 'accountant', 'dentist', 'dental clinic', 'doctor', 'hospital', 
                'gym', 'fitness center', 'yoga studio', 'hair salon', 'beauty salon', 'spa', 'car repair', 
                'auto repair shop', 'car wash', 'marketing agency', 'advertising agency', 'web designer', 
                'software company', 'information technology', 'cleaning service', 'pest control', 
                'moving company', 'roofing contractor', 'painter', 'landscaper', 'bakery', 'hotel', 
                'insurance agency', 'event planner', 'photographer', 'caterer', 'florist', 'jeweler', 
                'boutique', 'clothing store', 'hardware store', 'furniture store', 'veterinarian'
            ]
            
            for cat in common_cats:
                # Use a fast word boundary search
                if re.search(r'\b' + re.escape(cat) + r'\b', html, re.IGNORECASE):
                    extracted["raw_category"] = cat
                    break

        return extracted
