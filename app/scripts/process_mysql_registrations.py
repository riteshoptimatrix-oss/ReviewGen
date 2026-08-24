import asyncio
import pymysql.cursors
import httpx
import logging
from typing import List

# Setup path so we can import from app
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.core.config import settings
from app.db.session import init_db, close_db, db
from app.services.bulk_processor import BulkProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def process_registrations(limit: int = None):
    # Initialize MongoDB connection for caching results
    await init_db()
    
    # Initialize HTTP client for scraper
    limits = httpx.Limits(max_keepalive_connections=50, max_connections=100)
    timeout = httpx.Timeout(settings.http_timeout_seconds)
    client = httpx.AsyncClient(
        limits=limits,
        timeout=timeout,
        follow_redirects=True,
        max_redirects=settings.max_redirects,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5"
        }
    )
    
    try:
        # Connect to MySQL database
        connection = pymysql.connect(
            host=settings.mysql_host,
            port=settings.mysql_port,
            user=settings.mysql_user,
            password=settings.mysql_password,
            database=settings.mysql_db,
            cursorclass=pymysql.cursors.DictCursor
        )
        
        urls_to_process: List[str] = []
        
        with connection.cursor() as cursor:
            # We are prioritizing google_review_link, and then google_url
            sql = "SELECT id, google_review_link, google_url, google_link, url, website FROM registration"
            cursor.execute(sql)
            results = cursor.fetchall()
            
            for row in results:
                # Try getting the best link available
                target_url = (
                    row.get('google_review_link') or 
                    row.get('google_url') or 
                    row.get('google_link')
                )
                
                if target_url and str(target_url).startswith('http'):
                    urls_to_process.append(target_url)
                    
        connection.close()
        
        # Optionally limit for testing
        if limit:
            urls_to_process = urls_to_process[:limit]
            
        logger.info(f"Found {len(urls_to_process)} URLs to process.")
        
        # Process the URLs
        processor = BulkProcessor(http_client=client)
        # Process in batches to avoid taking up too much memory
        batch_size = 50
        for i in range(0, len(urls_to_process), batch_size):
            batch = urls_to_process[i:i+batch_size]
            logger.info(f"Processing batch {i//batch_size + 1} ({len(batch)} URLs)...")
            results = await processor.process_batch(batch, db)
            
            # Count success/failure
            success = sum(1 for r in results if r.success)
            failed = len(results) - success
            logger.info(f"Batch results: {success} successful, {failed} failed.")
            
    except Exception as e:
        logger.error(f"Error processing registrations: {e}")
    finally:
        await client.aclose()
        await close_db()

if __name__ == "__main__":
    # If you want to process all, set limit=None
    asyncio.run(process_registrations(limit=5))
