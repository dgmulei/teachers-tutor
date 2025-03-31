"""
Configuration and environment variables for the AI Teaching Assistant Platform.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

# OpenAI API settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Supabase settings
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_DB_PASSWORD = os.getenv("SUPABASE_DB_PASSWORD")

# Application settings
APP_NAME = os.getenv("APP_NAME", "AI Teaching Assistant")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# File upload settings
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt", ".md"}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB

# OpenAI model settings
ASSISTANT_MODEL = "gpt-4-turbo-preview"
EMBEDDING_MODEL = "text-embedding-3-small"

# Chat settings
MAX_THREAD_MESSAGES = 100
MAX_MESSAGE_LENGTH = 4000
