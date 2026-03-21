"""
Command-line interface module for the website-to-markdown tool.
"""
import os
import sys
import json
import asyncio
import argparse
from typing import List, Dict, Any
from pathlib import Path

from .crawler import setup_crawler, crawl_url, convert_website_to_markdown
from .chunk_processor import init_openai, process_document_with_docling
from .db import init_db, get_or_create_table, insert_chunks

async def process_and_store_document(url: str, content: str, db_table, is_test_mode: bool = False, dry_run: bool = False):
    """
    Process a document and store its chunks in the database.
    
    Args:
        url: Source URL of the document
        content: HTML or markdown content of the document
        db_table: LanceDB table reference
        is_test_mode: If True, skip LLM calls for titles, summaries and embeddings
        dry_run: If True, don't actually insert data, just simulate
        
    Returns:
        List of processed document chunks
    """
    # Process document using Docling
    processed_chunks = await process_document_with_docling(url, content, is_test_mode)
    
    if not processed_chunks:
        print(f"No chunks generated for {url}")
        return []
    
    # Store chunks in parallel
    await insert_chunks(processed_chunks, db_table, dry_run)
    
    return processed_chunks

async def crawl_parallel(urls: List[str], db_table, max_concurrent: int = 5, is_test_mode: bool = False, dry_run: bool = False):
    """
    Crawl multiple URLs in parallel with a concurrency limit.
    
    Args:
        urls: List of URLs to crawl
        db_table: LanceDB table reference 
        max_concurrent: Maximum number of concurrent crawling tasks
        is_test_mode: If True, skip LLM calls for titles, summaries and embeddings
        dry_run: If True, don't actually insert data, just simulate
        
    Returns:
        List of processed document chunks from all URLs
    """
    crawler = await setup_crawler()

    try:
        # Create a semaphore to limit concurrency
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_url(url: str):
            """Process a single URL with semaphore control."""
            async with semaphore:
                content = await crawl_url(crawler, url)
                
                if not content:
                    return []
                
                # Use HTML if available, otherwise use markdown
                if content['html']:
                    return await process_and_store_document(url, content['html'], db_table, is_test_mode, dry_run)
                elif content['markdown']:
                    return await process_and_store_document(url, content['markdown'], db_table, is_test_mode, dry_run)
                else:
                    print(f"No content available for: {url}")
                    return []
        
        # Process all URLs in parallel with limited concurrency
        results = await asyncio.gather(*[process_url(url) for url in urls])
        # Flatten the list of lists
        return [chunk for chunks in results if chunks for chunk in chunks]
    finally:
        await crawler.close()

async def test_processing(url: str, output_file: str, use_html: bool = True):
    """
    Test the document processing pipeline with a single URL.
    
    Args:
        url: URL to test processing on
        output_file: File path to save processing results
        use_html: If True, prefer HTML content over markdown
    """
    print(f"Testing with URL: {url}")
    
    # Create the crawler instance
    crawler = await setup_crawler(verbose=True)
    
    try:
        content = await crawl_url(crawler, url, session_id="test")
        
        if not content:
            print("Failed to crawl URL")
            return
            
        # Process document - use HTML if requested and available, otherwise use markdown
        doc_content = None
        if use_html and content['html']:
            doc_content = content['html']
            content_type = "HTML"
        elif content['markdown']:
            doc_content = content['markdown']
            content_type = "Markdown"
        else:
            print("No usable content found from crawler")
            return
            
        print(f"Using {content_type} content for processing")
        
        chunks = await process_document_with_docling(
            url, 
            doc_content,
            is_test_mode=True
        )
        
        # Print chunk info
        print(f"Generated {len(chunks)} chunks")
        for chunk in chunks:
            print(f"Chunk {chunk.chunk_number}:")
            print(f"Title: {chunk.title}")
            print(f"Summary: {chunk.summary}")
            print(f"Content: {chunk.content[:200]}...")  # Print first 200 characters of content
            print(f"Metadata: {json.dumps(chunk.metadata, indent=2)}")
            print(f"Embedding: {chunk.embedding[:10]}...")  # Print first 10 dimensions of embedding
            print("-" * 80)
        
        # Save chunks to output file
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump([{k: v for k, v in chunk.__dict__.items() if k != 'embedding'} for chunk in chunks], 
                     f, indent=2, default=str)
        
        print(f"Chunks saved to {output_file}")
    finally:
        await crawler.close()

async def main_cli():
    """
    Main CLI entry point for the application.
    
    Parses command-line arguments and executes the appropriate functionality.
    """
    parser = argparse.ArgumentParser(description="Crawl web documents and store chunks in LanceDB or convert websites to markdown")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Create 'convert' command
    convert_parser = subparsers.add_parser("convert", help="Convert a website to markdown")
    convert_parser.add_argument("website", help="Website URL to convert to markdown")
    convert_parser.add_argument("--output", dest="markdown_output", default="output.md", help="Output markdown file path")
    
    # Create 'test' command
    test_parser = subparsers.add_parser("test", help="Test processing with a single URL")
    test_parser.add_argument("url", help="URL to test processing on")
    test_parser.add_argument("--output", default="test_chunks.json", help="Output file for test results")
    test_parser.add_argument("--use-html", action="store_true", help="Use HTML content instead of markdown")
    
    # Create 'process' command
    process_parser = subparsers.add_parser("process", help="Process URLs and store chunks in database")
    process_parser.add_argument("urls", nargs="+", help="URLs to process")
    process_parser.add_argument("--dry-run", action="store_true", help="Process documents but don't insert into database")
    process_parser.add_argument("--db-path", help="Path to LanceDB database")
    process_parser.add_argument("--table-name", default="document_chunks", help="Name of the LanceDB table")
    
    args = parser.parse_args()
    
    # Show help message if no command is provided
    if not args.command:
        parser.print_help()
        return
        
    # Initialize OpenAI
    init_openai()
    
    # Handle website-to-markdown conversion
    if args.command == "convert":
        success = await convert_website_to_markdown(args.website, args.markdown_output)
        if success:
            print(f"Website successfully converted to markdown: {args.markdown_output}")
        return
    
    # Handle test command
    elif args.command == "test":
        await test_processing(args.url, args.output, args.use_html)
        return
        
    # Handle process command
    elif args.command == "process":
        # Initialize LanceDB
        db = init_db(args.db_path) if args.db_path else init_db()
        table = get_or_create_table(db, args.table_name)
        
        print(f"Processing {len(args.urls)} URLs")
        chunks = await crawl_parallel(args.urls, table, is_test_mode=False, dry_run=args.dry_run)
        print(f"Processed {len(chunks)} chunks total")
        print(f"LanceDB table '{args.table_name}' now has {table.count_rows()} rows")

def run_cli():
    """
    Entry point for CLI script defined in pyproject.toml
    """
    asyncio.run(main_cli())

if __name__ == "__main__":
    run_cli()
