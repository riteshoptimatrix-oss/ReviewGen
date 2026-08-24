from bs4 import BeautifulSoup
from typing import Dict, Any, Optional
from app.schemas.business import BusinessData
from app.services.structured_data_extractor import StructuredDataExtractor
from app.services.metadata_extractor import MetadataExtractor
from app.services.embedded_data_extractor import EmbeddedDataExtractor
from app.core.logging import logger
from app.core.exceptions import ExtractionFailedError

class BusinessExtractor:
    
    @classmethod
    def extract(cls, html: str, input_url: str, final_url: str) -> BusinessData:
        """
        Orchestrates extraction prioritizing JSON-LD > Meta > Embedded Data.
        """
        soup = BeautifulSoup(html, "lxml")
        
        json_ld_data = StructuredDataExtractor.extract(soup)
        meta_data = MetadataExtractor.extract(soup)
        embedded_data = EmbeddedDataExtractor.extract(soup, html)
        
        business_name = cls._select_best_value(
            "business_name", 
            [json_ld_data, meta_data, embedded_data]
        )
        
        raw_category = cls._select_best_value(
            "raw_category", 
            [json_ld_data, embedded_data]
        )
        
        address = cls._select_best_value(
            "address", 
            [json_ld_data, embedded_data]
        )
        
        phone = cls._select_best_value(
            "phone", 
            [json_ld_data, embedded_data]
        )
        
        website = cls._select_best_value(
            "website", 
            [json_ld_data, embedded_data]
        )
        
        rating = cls._select_best_value(
            "rating", 
            [json_ld_data]
        )
        
        review_count = cls._select_best_value(
            "review_count", 
            [json_ld_data]
        )
        
        return BusinessData(
            input_url=input_url,
            final_url=final_url,
            business_name=business_name,
            raw_category=raw_category,
            address=address,
            phone=phone,
            website=website,
            rating=rating,
            review_count=review_count
        )
        
    @classmethod
    def _select_best_value(cls, key: str, sources: list) -> Optional[Any]:
        """
        Takes the first available value from the sources in order.
        """
        for source in sources:
            val = source.get(key)
            if val is not None and val != "":
                return val
        return None
