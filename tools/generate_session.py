"""
This script generates a Telethon .session file for project authentication.
Run this file from the terminal when setting up your project.
"""

import os
import sys

from dotenv import load_dotenv
from telethon import TelegramClient

from utils.logger import Logger

load_dotenv()

logger = Logger(visible_level="info")

api_id, api_hash, phone, session_name = (
    os.getenv("API_ID"),
    os.getenv("API_HASH"),
    os.getenv("PHONE"),
    os.getenv("SESSION_NAME"),
)
if not api_id or not api_hash or not phone or not session_name:
    logger.print(
        "API_ID, API_HASH, PHONE, and/or SESSION_NAME not found. Please set them in environment variables or config.env.",
        section_name="setup",
        level="error",
    )
    sys.exit(1)

try:
    client = TelegramClient(session_name, api_id, api_hash)
    client.start(phone=phone)
    logger.print(
        f'Session file "{session_name}.session" created successfully!',
        section_name="setup",
        level="info",
    )
except (ValueError, TypeError) as e:
    logger.print(f"Input Error: {e}", section_name="setup", level="error")
except ImportError as e:
    logger.print(f"Import Error: {e}", section_name="setup", level="error")
except ConnectionError as e:
    logger.print(f"Connection Error: {e}", section_name="setup", level="error")
except RuntimeError as e:
    logger.print(f"Runtime Error: {e}", section_name="setup", level="error")
