"""
Document processing module for processing HTML/Markdown content into chunks.
"""
import os
import sys
import json
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from urllib.parse import urlparse
from pathlib import Path
import io

# Ensure project imports work
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from openai import AsyncOpenAI
from docling.document_converter import DocumentConverter, InputFormat, DocumentStream
from docling.chunking import HybridChunker

# Import local utils with a more robust approach
try:
    # Try relative import first (when installed as package)
    from ..utils.tokenizer import OpenAITokenizerWrapper
    from .models import ProcessedChunk
    from .config import OPENAI_API_KEY, LLM_MODEL, EMBEDDING_MODEL, EMBEDDING_DIMENSIONS, MAX_CHUNK_TOKENS
except ImportError:
    try:
        # Try absolute import (when running from source)
        from src.utils.tokenizer import OpenAITokenizerWrapper
        from src.website_pipeline.models import ProcessedChunk
        from src.website_pipeline.config import OPENAI_API_KEY, LLM_MODEL, EMBEDDING_MODEL, EMBEDDING_DIMENSIONS, MAX_CHUNK_TOKENS
    except ImportError:
        # Fall back to direct import (when running from project root)
        sys.path.append(str(project_root))
        from src.utils.tokenizer import OpenAITokenizerWrapper
        from src.website_pipeline.models import ProcessedChunk
        from src.website_pipeline.config import OPENAI_API_KEY, LLM_MODEL, EMBEDDING_MODEL, EMBEDDING_DIMENSIONS, MAX_CHUNK_TOKENS

# Initialize OpenAI client
openai_client = None

def init_openai(api_key: str = None):
    """Initialize the OpenAI client with the given API key."""
    global openai_client
    api_key = api_key or OPENAI_API_KEY
    if not api_key:
        print("Warning: No OpenAI API key provided. Some features will be disabled.")
    openai_client = AsyncOpenAI(api_key=api_key)

async def get_title_and_summary(chunk: str, url: str) -> Dict[str, str]:
    """
    Extract title and summary from a document chunk using LLM.
    
    Args:
        chunk: Text content of the document chunk
        url: Source URL of the document
        
    Returns:
        Dictionary containing 'title' and 'summary' keys
        
    Raises:
        Exception: If there's an error in the API call or parsing response
    """
    if not openai_client:
        return {"title": "Title extraction disabled - no API key", "summary": "Summary disabled - no API key"}
    
    system_prompt = """You are an AI that extracts titles and summaries from documentation chunks.
    Return a JSON object with 'title' and 'summary' keys.
    For the title: If this seems like the start of a document, extract its title. If it's a middle chunk, derive a descriptive title.
    For the summary: Create a concise summary of the main points in this chunk.
    Keep both title and summary concise but informative."""
    
    try:
        response = await openai_client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"URL: {url}\n\nContent:\n{chunk[:1000]}..."}  # Send first 1000 chars for context
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Error getting title and summary: {e}")
        return {"title": "Error processing title", "summary": "Error processing summary"}

async def get_embedding(text: str) -> List[float]:
    """
    Generate an embedding vector for the given text using OpenAI's API.
    
    Args:
        text: Text content to embed
        
    Returns:
        List of floating point values representing the embedding vector
        
    Raises:
        Exception: If there's an error in the API call, returns a zero vector
    """
    if not openai_client:
        return [0] * EMBEDDING_DIMENSIONS  # Return zero vector if no API key
        
    try:
        response = await openai_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error getting embedding: {e}")
        return [0] * EMBEDDING_DIMENSIONS  # Return zero vector on error

async def process_document_with_docling(url: str, content: str, is_test_mode: bool = False) -> List[ProcessedChunk]:
    """
    Process a document using Docling's document processing pipeline.
    
    Args:
        url: Source URL of the document
        content: HTML or markdown content of the document
        is_test_mode: If True, skip LLM calls for titles, summaries and embeddings
        
    Returns:
        List of ProcessedChunk objects representing the document chunks
        
    Raises:
        Exception: If there's an error in document conversion or chunking
    """
    print(f"Processing document with Docling: {url}")
    
    # Initialize the document converter with specific format options
    converter = DocumentConverter(
        allowed_formats=[InputFormat.HTML, InputFormat.MD]
    )
    
    # Check if content is from HTML or Markdown based on content signatures
    is_html = "<html" in content.lower() or "<body" in content.lower()
    
    try:
        # Create a temporary file for conversion
        temp_file = f"temp_content_{url.split('/')[-1]}.{'html' if is_html else 'md'}"
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Set headers with content type
        headers = {"Content-Type": "text/html" if is_html else "text/markdown"}
        
        # Convert using file path instead of DocumentStream
        result = converter.convert(
            source=temp_file,
            headers=headers,
            raises_on_error=False
        )
        
        # Clean up temporary file
        try:
            os.remove(temp_file)
        except Exception as e:
            print(f"Warning: Failed to remove temporary file: {e}")
            
        if not result.document:
            print(f"Failed to convert document: {url}")
            if result.errors:
                print(f"Conversion errors: {', '.join(str(e) for e in result.errors)}")
            return []
    except Exception as e:
        print(f"Exception during document conversion: {str(e)}")
        return []
    
    # Initialize the tokenizer and chunker
    tokenizer = OpenAITokenizerWrapper()
    chunker = HybridChunker(
        tokenizer=tokenizer,
        max_tokens=MAX_CHUNK_TOKENS,  # Using config value instead of hardcoded value
        merge_peers=True,
    )
    
    # Extract chunks using Docling's HybridChunker
    try:
        chunks = list(chunker.chunk(dl_doc=result.document))
        print(f"Generated {len(chunks)} chunks with Docling")
    except Exception as e:
        print(f"Exception during chunking: {str(e)}")
        return []
    
    processed_chunks = []
    for i, chunk in enumerate(chunks):
        # Extract title from headings or generate one
        title = chunk.meta.headings[0] if chunk.meta.headings else f"Section {i+1}"
        
        # Get page numbers if available
        page_numbers = sorted(set(
            prov.page_no for item in chunk.meta.doc_items 
            for prov in item.prov if hasattr(prov, 'page_no')
        )) or None
        
        # Generate summary or use placeholder in test mode
        summary = ""
        if not is_test_mode:
            extracted = await get_title_and_summary(chunk.text, url)
            title = extracted.get('title', title)
            summary = extracted.get('summary', "")
        else:
            summary = "Test summary - not sent to LLM in test mode"
        
        # Get embedding or use placeholder in test mode
        embedding = []
        if not is_test_mode:
            embedding = await get_embedding(chunk.text)
        else:
            embedding = [0.0] * EMBEDDING_DIMENSIONS  # Using config value for embedding dimensions
        
        # Build metadata
        metadata = {
            "source": "document_chunks",
            "chunk_size": len(chunk.text),
            "crawled_at": datetime.now(timezone.utc).isoformat(),
            "url_path": urlparse(url).path,
            "headings": chunk.meta.headings,
            "page_numbers": page_numbers,
            "chunker": "docling_hybrid",
            "document_status": result.status,
            "format": "html" if is_html else "markdown"
        }
        
        processed_chunk = ProcessedChunk(
            url=url,
            chunk_number=i,
            title=title,
            summary=summary,
            content=chunk.text,
            metadata=metadata,
            embedding=embedding
        )
        
        processed_chunks.append(processed_chunk)
        
    return processed_chunks
