# Website to Markdown

A tool for converting websites to markdown and processing web documents.

## Overview

This project provides tools to crawl websites, convert HTML pages to markdown, process the content through chunking, and enable efficient storage and retrieval of the content.

## Configuration

The application uses a centralized configuration system managed through `src/website_pipeline/config.py`. Configuration values can be set through:

1. **Environment variables**: Set directly in your environment
2. **dotenv file**: Create a `.env` file in the root directory of the project
3. **Default values**: Fallback values defined in the code

### Setting Up Environment Variables

1. Copy the `.env.example` file to a new file named `.env` in the project root:
   ```bash
   cp .env.example .env
   ```
2. Edit the `.env` file to set your specific configuration values:
   ```bash
   # Open with your favorite editor
   nano .env
   ```
3. At minimum, add your OpenAI API key:
   ```
   OPENAI_API_KEY=sk-your-api-key-here
   ```

### Key Configuration Parameters

| Parameter | Environment Variable | Default | Description |
|-----------|---------------------|---------|-------------|
| Database Path | `DB_PATH` | `./data/documents.db` | Path to SQLite database |
| LanceDB URI | `LANCEDB_URI` | `./data/lancedb` | Path to LanceDB vector database |
| OpenAI API Key | `OPENAI_API_KEY` | None | Your OpenAI API key |
| LLM Model | `LLM_MODEL` | `gpt-4o-mini` | Model to use for text generation |
| Embedding Model | `EMBEDDING_MODEL` | `text-embedding-3-small` | Model for creating embeddings |
| Max Chunk Tokens | `MAX_CHUNK_TOKENS` | 8191 | Maximum tokens per chunk |
| Crawl Delay | `CRAWL_DELAY` | 0.5 | Seconds between requests |
| User Agent | `USER_AGENT` | `WebsiteToMarkdown/0.1.0` | User agent for web requests |
| Max Pages | `MAX_PAGES` | 100 | Maximum pages to crawl per domain |
| Test Mode | `TEST_MODE` | `false` | Set to `true` to skip API calls |

### Example .env File

