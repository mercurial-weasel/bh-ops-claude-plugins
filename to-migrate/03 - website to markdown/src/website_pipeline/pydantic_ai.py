"""
Module containing Pydantic AI specific code.
Functions for working with the Pydantic AI documentation website.
"""
import re
from typing import List, Dict, Any


def get_pydantic_ai_docs_urls() -> List[str]:
    """
    Get URLs from Pydantic AI docs sitemap.
    
    Returns:
        List of URLs extracted from the sitemap
    """
    sitemap_url = "https://ai.pydantic.dev/sitemap.xml"
    try:
        import requests
        from xml.etree import ElementTree
        
        response = requests.get(sitemap_url)
        response.raise_for_status()
        
        # Parse the XML
        root = ElementTree.fromstring(response.content)
        
        # Extract all URLs from the sitemap
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = [loc.text for loc in root.findall('.//ns:loc', namespace)]
        
        return urls
    except Exception as e:
        print(f"Error fetching sitemap: {e}")
        # Fall back to a list of known URLs if sitemap fails
        base_url = "https://ai.pydantic.dev"
        paths = [
            "/",  # Main page
            "/getting-started/",
            "/usage/",
            "/usage/modes/",
            "/usage/schema/",
            "/usage/requests/",
            "/usage/responses/",
            "/usage/performance/",
            "/examples/",
            "/api-reference/",
            "/api-reference/core/",
            "/api-reference/providers/",
            "/release-notes/",
        ]
        return [f"{base_url}{path}" for path in paths]


async def crawl_pydantic_docs(crawler, db_table, is_test_mode: bool = False, dry_run: bool = False):
    """
    Crawl the Pydantic AI documentation website and store chunks in database.
    
    Args:
        crawler: Crawler instance
        db_table: LanceDB table reference
        is_test_mode: If True, skip LLM calls for titles, summaries and embeddings
        dry_run: If True, don't actually insert data, just simulate
        
    Returns:
        List of processed document chunks
    """
    from .cli import crawl_parallel
    
    # Get URLs to crawl
    urls = get_pydantic_ai_docs_urls()
    
    print(f"Crawling {len(urls)} URLs from Pydantic AI docs")
    
    # Use the parallel crawler function from CLI
    return await crawl_parallel(urls, db_table, is_test_mode=is_test_mode, dry_run=dry_run)
