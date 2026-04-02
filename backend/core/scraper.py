import aiohttp
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

async def scrape_url(url: str) -> dict:
    """
    Scrapes a given business URL to extract the title, meta description, and main text content.
    """
    logger.info(f"Scraping URL: {url}")
    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            async with session.get(url, timeout=10) as response:
                response.raise_for_status()
                html = await response.text()

        soup = BeautifulSoup(html, "html.parser")
        
        # Extract title
        title = soup.title.string if soup.title else ""
        
        # Extract meta description
        meta_desc = ""
        meta_tag = soup.find("meta", attrs={"name": "description"})
        if meta_tag and "content" in meta_tag.attrs:
            meta_desc = meta_tag["content"]

        # Extract visible text (basic attempt)
        for script in soup(["script", "style", "nav", "footer"]):
            script.decompose()
            
        text = soup.get_text(separator=" ", strip=True)
        # Limit text length to avoid token limits for basic scraping
        text = text[:5000]

        return {
            "url": url,
            "title": title.strip(),
            "description": meta_desc.strip(),
            "content": text
        }
    except Exception as e:
        logger.error(f"Failed to scrape {url}: {e}")
        return {
            "url": url,
            "title": "Unknown",
            "description": "Failed to scrape description",
            "content": f"Failed to scrape content due to error: {e}"
        }
