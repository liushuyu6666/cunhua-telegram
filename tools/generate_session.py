"""
This script generates a Telethon .session file for project authentication.
Run this file from the terminal when setting up your project.
"""

from telethon import TelegramClient
from utils.logger import Logger


logger = Logger(visible_level="info")

api_id = input("Enter your API ID: ")
api_hash = input("Enter your API Hash: ")
phone = input("Enter your phone number (e.g. +1234567890): ")
session_name = (
    input("Enter a name for your session file (default: my_session): ").strip()
    or "my_session"
)


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
