import asyncio
import httpx
from bs4 import BeautifulSoup
import urllib.parse

async def main():
    async with httpx.AsyncClient(headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}) as client:
        businessName = "Optimatrix Solutions   Website Design Company"
        url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(businessName + " category")
        resp = await client.get(url)
        soup = BeautifulSoup(resp.text, "lxml")
        
        for a in soup.find_all("a", class_="result__snippet"):
            print("Snippet:", a.text)

asyncio.run(main())
