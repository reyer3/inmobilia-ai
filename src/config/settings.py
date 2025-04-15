"""Configuration settings for the application."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Application settings
APP_NAME = "Inmobilia AI"
APP_VERSION = "0.1.0"
DEBUG = os.getenv("DEBUG", "False").lower() in ["true", "1"]

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Database settings
DATABASE_URL = os.getenv("DATABASE_URL")

# Validation
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set. Please set it in your .env file.")