"""
Main entry point for the website to markdown tool.
"""
import os
import sys
from pathlib import Path

# Add the project root to the Python path to enable imports
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Update import path to the correct location
try:
    from src.website_pipeline.cli import run_cli
except ImportError:
    # If that fails, try direct import (when package is installed)
    try:
        from website_pipeline.cli import run_cli
    except ImportError:
        print("Error: Unable to import the CLI module.")
        print("Make sure the cli.py file exists in the src/website_pipeline directory.")
        sys.exit(1)

if __name__ == "__main__":
    run_cli()
