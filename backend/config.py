"""Configuration settings for the CMYK Splitter backend."""

import os

# Debug mode - enables verbose logging and saves debug files
# Set DEBUG=1 or DEBUG=true to enable
DEBUG = os.getenv("DEBUG", "").lower() in ("1", "true", "yes", "on")

# Debug output directory
DEBUG_DIR = "backend/services/debug_files"
