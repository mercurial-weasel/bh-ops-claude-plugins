"""
Centralized configuration for the website pipeline.
Manages environment variables, API keys, and other configuration settings.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
dotenv_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=dotenv_path)

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = os.getenv("DATA_DIR", str(PROJECT_ROOT / "data"))

# Database configuration
DB_PATH = os.getenv("DB_PATH", str(Path(DATA_DIR) / "documents.db"))
LANCEDB_URI = os.getenv("LANCEDB_URI", str(Path(DATA_DIR) / "lancedb"))

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Model configurations
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")  
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
EMBEDDING_DIMENSIONS = 1536  # Dimension for text-embedding-3-small

# Chunking settings
MAX_CHUNK_TOKENS = int(os.getenv("MAX_CHUNK_TOKENS", "8191"))  # Default for compatibility with embedding models

# Crawler settings
CRAWL_DELAY = float(os.getenv("CRAWL_DELAY", "0.5"))  # Delay between requests in seconds
USER_AGENT = os.getenv("USER_AGENT", "WebsiteToMarkdown/0.1.0 (Educational Purpose)")
MAX_PAGES = int(os.getenv("MAX_PAGES", "100"))  # Maximum pages to crawl per domain

# Flag for test mode (skips API calls)
TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"

def get_config_dict():
    """Return all configuration values as a dictionary for logging/debugging."""
    return {k: v for k, v in globals().items() 
            if k.isupper() and not k.startswith("_")}

# Print a message if no OpenAI API key is found
if not OPENAI_API_KEY:
    print("Warning: No OpenAI API key found in environment variables or .env file.")
    print("Some features will be disabled. Set OPENAI_API_KEY in your .env file.")
