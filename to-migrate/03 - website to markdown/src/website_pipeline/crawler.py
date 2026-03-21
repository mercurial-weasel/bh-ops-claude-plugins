"""
Web crawling module for fetching web content and converting to markdown.
"""
import os
from typing import List, Optional
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from .pydantic_ai import get_pydantic_ai_docs_urls

async def setup_crawler(verbose: bool = False) -> AsyncWebCrawler:
    """
    Set up and start a web crawler instance.
    
    Args:
        verbose: Whether to enable verbose logging for the crawler
        
    Returns:
        AsyncWebCrawler instance that has been started
    """
    browser_config = BrowserConfig(
        headless=True,
        verbose=verbose,
        extra_args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"],
    )
    
    crawler = AsyncWebCrawler(config=browser_config)
    await crawler.start()
    return crawler

async def crawl_url(crawler: AsyncWebCrawler, url: str, session_id: str = "default") -> Optional[dict]:
    """
    Crawl a URL and return the content if successful.
    
    Args:
        crawler: AsyncWebCrawler instance
        url: URL to crawl
        session_id: Identifier for the crawl session
        
    Returns:
        Dictionary with 'html' and 'markdown' keys if successful, None otherwise
    """
    crawl_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)
    
    result = await crawler.arun(
        url=url,
        config=crawl_config,
        session_id=session_id
    )
    
    if result.success:
        # Use the updated markdown attribute instead of the deprecated markdown_v2
        markdown_content = None
        if hasattr(result, 'markdown') and result.markdown:
            markdown_content = result.markdown.raw_markdown
            
        return {
            'html': result.html,
            'markdown': markdown_content,
            'url': url
        }
    else:
        print(f"Failed to crawl {url}: {result.error_message}")
        return None

async def convert_website_to_markdown(url: str, output_file: str) -> bool:
    """
    Convert a website to markdown and save it to a file.
    
    Args:
        url: Website URL to convert
        output_file: File path to save the markdown content
        
    Returns:
        Boolean indicating success or failure
    """
    print(f"Converting website {url} to markdown...")
    
    crawler = await setup_crawler(verbose=True)
    
    try:
        content = await crawl_url(crawler, url, session_id="convert")
        
        if not content:
            return False
            
        if content['markdown']:
            markdown_content = content['markdown']
            
            # Save markdown to output file
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(markdown_content)
            
            print(f"Markdown content saved to {output_file}")
            print(f"Content length: {len(markdown_content)} characters")
            
            # Show a preview
            preview_length = min(200, len(markdown_content))
            print(f"Preview:\n{markdown_content[:preview_length]}...")
            
            return True
        else:
            print("No markdown content was generated")
            return False
    finally:
        await crawler.close()
