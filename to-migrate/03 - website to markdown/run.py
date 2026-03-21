"""
Simple wrapper script to run the website-to-markdown tool from the project root.
"""
import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Update the import path to the correct location
try:
    from src.website_pipeline.cli import run_cli
except ImportError:
    try:
        from website_pipeline.cli import run_cli
    except ImportError:
        print("Error: Unable to import the CLI module.")
        print("Make sure the cli.py file exists in the src/website_pipeline directory.")
        sys.exit(1)

if __name__ == "__main__":
    run_cli()
