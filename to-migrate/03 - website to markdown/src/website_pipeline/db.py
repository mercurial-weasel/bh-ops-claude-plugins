"""
Database operations module for storing and retrieving document chunks.
"""
import os
import json
import asyncio
from typing import List, Dict, Any, Optional
import lancedb
from lancedb.pydantic import LanceModel, Vector
from pathlib import Path
from .chunk_processor import ProcessedChunk

# Set the default database path
DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "lancedb")

class RawDocChunk(LanceModel):
    """
    Schema for document chunks stored in LanceDB.
    
    Attributes:
        url: Source URL of the document
        chunk_number: Sequential number of the chunk within the document
        title: Title or heading of the chunk
        summary: Brief summary of the chunk's content
        content: Full text content of the chunk
        metadata_json: JSON string containing metadata about the chunk
        embedding: Vector embedding of the chunk content for semantic search
    """
    url: str
    chunk_number: int
    title: str
    summary: str
    content: str
    metadata_json: str  # Store metadata as a JSON string instead of Dict
    embedding: Vector(1536)  # OpenAI embeddings are 1536 dimensions

def init_db(db_path: str = DEFAULT_DB_PATH) -> lancedb.db.LanceTable:
    """
    Initialize the LanceDB database and ensure the path exists.
    
    Args:
        db_path: Path to LanceDB database directory
        
    Returns:
        LanceDB database instance
    """
    os.makedirs(db_path, exist_ok=True)
    return lancedb.connect(db_path)

def get_or_create_table(db, table_name: str = "document_chunks") -> lancedb.db.LanceTable:
    """
    Get an existing table or create a new one if it doesn't exist.
    
    Args:
        db: LanceDB database instance
        table_name: Name of the table to get or create
        
    Returns:
        LanceDB table instance
    """
    try:
        table = db.open_table(table_name)
        print(f"Opened existing table '{table_name}'")
    except:
        print(f"Creating new table '{table_name}'")
        table = db.create_table(table_name, schema=RawDocChunk, mode="overwrite")
    
    return table

async def insert_chunk(chunk: ProcessedChunk, db_table, dry_run: bool = False) -> Optional[Dict[str, Any]]:
    """
    Insert a processed chunk into LanceDB.
    
    Args:
        chunk: ProcessedChunk object to insert
        db_table: LanceDB table reference
        dry_run: If True, don't actually insert data, just simulate
        
    Returns:
        Dictionary of inserted data or None if an error occurred
    """
    try:
        # Convert metadata to JSON string
        metadata_json = json.dumps(chunk.metadata, default=str)
        
        data = {
            "url": chunk.url,
            "chunk_number": chunk.chunk_number,
            "title": chunk.title,
            "summary": chunk.summary,
            "content": chunk.content,
            "metadata_json": metadata_json,  # Store as JSON string
            "embedding": chunk.embedding
        }
        
        if dry_run:
            print(f"[DRY RUN] Would insert chunk {chunk.chunk_number} for {chunk.url}")
            return data
        
        # Add data to LanceDB table
        db_table.add([data])
        print(f"Inserted chunk {chunk.chunk_number} for {chunk.url}")
        return data
    except Exception as e:
        print(f"Error inserting chunk: {e}")
        return None

async def insert_chunks(chunks: List[ProcessedChunk], db_table, dry_run: bool = False) -> List[Optional[Dict[str, Any]]]:
    """
    Insert multiple chunks into LanceDB in parallel.
    
    Args:
        chunks: List of ProcessedChunk objects to insert
        db_table: LanceDB table reference
        dry_run: If True, don't actually insert data, just simulate
        
    Returns:
        List of dictionaries or None values for each chunk insertion
    """
    insert_tasks = [
        insert_chunk(chunk, db_table, dry_run) 
        for chunk in chunks
    ]
    return await asyncio.gather(*insert_tasks)
