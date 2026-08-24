import asyncio
import httpx
from bs4 import BeautifulSoup
from app.utils.url_utils import validate_google_url
from app.services.google_resolver import GoogleResolver
from app.services.business_extractor import BusinessExtractor

async def main():
    async with httpx.AsyncClient(follow_redirects=True) as client:
        url = "https://g.page/r/CdsN6Zff3D7IEBM/review"
        validated_url = validate_google_url(url)
        print("Validated URL:", validated_url)
        
        resolver = GoogleResolver(client)
        result = await resolver.resolve(validated_url)
        print("Final URL:", result.final_url)
        
        extracted = BusinessExtractor.extract(result.html, result.input_url, result.final_url)
        print("Extracted Data:", extracted.model_dump())

asyncio.run(main())
