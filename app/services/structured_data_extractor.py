import json
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Optional
from app.core.logging import logger
from app.utils.text_utils import clean_text

class StructuredDataExtractor:
    
    @classmethod
    def extract(cls, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Extracts JSON-LD structured data from the HTML.
        Handles single objects, lists, and @graph structures.
        """
        results = []
        scripts = soup.find_all("script", type="application/ld+json")
        
        for script in scripts:
            if not script.string:
                continue
            try:
                data = json.loads(script.string)
                if isinstance(data, list):
                    results.extend(data)
                elif isinstance(data, dict):
                    if "@graph" in data and isinstance(data["@graph"], list):
                        results.extend(data["@graph"])
                    else:
                        results.append(data)
            except json.JSONDecodeError:
                logger.warning("Failed to decode JSON-LD script.")
                continue

        extracted = {}
        # Prioritize LocalBusiness or subtypes
        local_business = cls._find_by_type(results, ["LocalBusiness", "Restaurant", "Store", "Organization"])
        if local_business:
            extracted["business_name"] = clean_text(local_business.get("name"))
            extracted["phone"] = clean_text(local_business.get("telephone"))
            extracted["website"] = clean_text(local_business.get("url"))
            
            # Category might be in @type or separate category field
            category = local_business.get("@type")
            if isinstance(category, list):
                category = category[0] if category else None
            extracted["raw_category"] = clean_text(category) if category != "LocalBusiness" else None

            # Rating
            agg_rating = local_business.get("aggregateRating")
            if isinstance(agg_rating, dict):
                try:
                    extracted["rating"] = float(agg_rating.get("ratingValue"))
                    extracted["review_count"] = int(agg_rating.get("reviewCount") or agg_rating.get("ratingCount"))
                except (ValueError, TypeError):
                    pass
            
            # Address
            address = local_business.get("address")
            if isinstance(address, dict):
                addr_parts = [
                    address.get("streetAddress"),
                    address.get("addressLocality"),
                    address.get("addressRegion"),
                    address.get("postalCode")
                ]
                extracted["address"] = clean_text(", ".join(filter(None, addr_parts)))
            elif isinstance(address, str):
                extracted["address"] = clean_text(address)
                
        return extracted
        
    @classmethod
    def _find_by_type(cls, items: List[Dict[str, Any]], types: List[str]) -> Optional[Dict[str, Any]]:
        """
        Find the best-matching item by priority type order.
        Iterates through the priority list first so Restaurant beats Organization.
        """
        for preferred_type in types:
            for item in items:
                item_type = item.get("@type")
                if isinstance(item_type, str) and item_type == preferred_type:
                    return item
                elif isinstance(item_type, list) and preferred_type in item_type:
                    return item
        return None
