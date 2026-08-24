import re
from typing import Optional
from app.schemas.common import ExtractedValue

class CategoryNormalizer:
    
    # Base taxonomy
    TAXONOMY = {
        "Software Company": ["software company", "software developer", "computer software company", "software"],
        "IT Services": ["it services", "information technology", "tech support"],
        "Marketing Agency": ["marketing agency", "marketing"],
        "Advertising Agency": ["advertising agency", "advertising"],
        "Clothing Store": ["clothing store", "clothing shop", "fashion store", "boutique", "clothes"],
        "Restaurant": ["restaurant", "indian restaurant", "italian restaurant", "fast food restaurant", "diner", "eatery"],
        "Cafe": ["cafe", "coffee shop", "coffeehouse", "espresso bar"],
        "Hotel": ["hotel", "motel", "inn", "resort"],
        "Real Estate": ["real estate", "real estate agency", "realtor"],
        "Law Firm": ["law firm", "lawyer", "attorney", "legal services"],
        "Accounting Firm": ["accounting firm", "accountant", "cpa"],
        "Medical Clinic": ["medical clinic", "clinic", "doctor"],
        "Dentist": ["dentist", "dental clinic"],
        "Hospital": ["hospital", "medical center"],
        "Pharmacy": ["pharmacy", "drugstore"],
        "Gym / Fitness": ["gym", "fitness center", "health club"],
        "Beauty Salon": ["beauty salon", "salon", "hair salon"],
        "Barber Shop": ["barber shop", "barber"],
        "Automotive": ["automotive", "auto"],
        "Car Dealer": ["car dealer", "dealership", "auto dealer"],
        "Repair Service": ["repair service", "mechanic", "auto repair"],
        "Education / Training": ["education", "training center", "tutoring"],
        "School": ["school", "high school", "elementary school"],
        "College / University": ["college", "university"],
        "Financial Services": ["financial services", "financial planner"],
        "Insurance Agency": ["insurance agency", "insurance broker"],
        "Travel Agency": ["travel agency", "travel agent"],
        "Construction": ["construction", "builder", "contractor"],
        "Home Services": ["home services", "plumber", "electrician", "hvac"],
        "Retail Store": ["retail store", "shop", "store"],
        "Grocery Store": ["grocery store", "supermarket", "market"],
        "Electronics Store": ["electronics store", "electronic parts supplier"],
        "Furniture Store": ["furniture store", "furniture"],
        "Photography": ["photography", "photographer", "photo studio"],
        "Event Services": ["event services", "event planner", "wedding planner"],
        "Other": []
    }

    @classmethod
    def normalize(cls, raw_category: Optional[str]) -> ExtractedValue:
        """
        Normalizes a raw category to the defined taxonomy.
        """
        if not raw_category:
            return ExtractedValue(value=None, source="google_category", confidence=0.0)
            
        raw_lower = raw_category.lower().strip()
        
        # 1. Exact match checking in normalized forms
        for normalized, synonyms in cls.TAXONOMY.items():
            if raw_lower == normalized.lower():
                return ExtractedValue(value=normalized, source="google_category", confidence=1.0)
            if raw_lower in synonyms:
                return ExtractedValue(value=normalized, source="google_category", confidence=0.95)
                
        # 2. Partial strong match (e.g., "Best Indian Restaurant" -> "Restaurant")
        best_match = None
        max_len = 0
        for normalized, synonyms in cls.TAXONOMY.items():
            for synonym in synonyms:
                if re.search(r'\b' + re.escape(synonym) + r'\b', raw_lower):
                    if len(synonym) > max_len:
                        max_len = len(synonym)
                        best_match = normalized
                        
        if best_match:
            return ExtractedValue(value=best_match, source="google_category", confidence=0.85)

        # 3. Fallback to Other or leave as is if we want to retain the raw value
        # The prompt says: "If no reliable category exists: normalized_category = null"
        # However, if we know it's a category from Google but it doesn't match our taxonomy,
        # we might just return None and let raw_category hold the original.
        return ExtractedValue(value=None, source="google_category", confidence=0.0)
