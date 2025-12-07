"""
Configuration file for Trello API Automated Tests.
Reads sensitive data from environment variables (.env file).
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base URL for Trello API
BASE_URL = "https://api.trello.com/1"


API_KEY = os.getenv("TRELLO_API_KEY")
API_TOKEN = os.getenv("TRELLO_API_TOKEN")

if not API_KEY or not API_TOKEN:
    raise ValueError("API Credentials not found! Please check your .env file.")

# Default Test Data
DEFAULT_BOARD_NAME = "Automated Test Board"
