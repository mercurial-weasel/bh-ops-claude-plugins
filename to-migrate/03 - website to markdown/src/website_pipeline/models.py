"""
Central module for data models used across the website pipeline.
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class ProcessedChunk:
    """
    Represents a processed document chunk with metadata and embedding.
    
    Attributes:
        url: Source URL of the document
        chunk_number: Sequential number of the chunk within the document
        title: Title or heading of the chunk
        summary: Brief summary of the chunk's content
        content: Full text content of the chunk
        metadata: Dictionary containing metadata about the chunk
        embedding: Vector representation of the chunk for semantic search
    """
    url: str
    chunk_number: int
    title: str
    summary: str
    content: str
    metadata: Dict[str, Any]
    embedding: List[float]

@dataclass
class RawDocChunk:
    """
    Represents a raw document chunk before processing.
    
    Note: This class is imported from db.py - the original docstring 
    should be preserved when available in the source file.
    """
    url: str
    content: str
    metadata: Dict[str, Any]
