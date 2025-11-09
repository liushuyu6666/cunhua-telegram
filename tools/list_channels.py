"""
This script lists all channels the user account has access to, including channel ID, name, and whether the channel is active.
Run this file from the terminal after generating your session file.
"""

import os
import sys

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.tl.types import Channel

from utils.logger import Logger

load_dotenv()

logger = Logger(visible_level="info")

session_name = (
    input("Enter your session file name (default: my_session): ").strip()
    or "my_session"
)
api_id, api_hash, phone, session_name = (
    os.getenv("API_ID"),
    os.getenv("API_HASH"),
    os.getenv("PHONE"),
    os.getenv("SESSION_NAME"),
)
if not api_id or not api_hash or not phone or not session_name:
    logger.print(
        "API_ID, API_HASH, PHONE, and/or SESSION_NAME not found. Please set them in environment variables or config.env.",
        section_name="list_channels",
        level="error",
    )
    sys.exit(1)

try:
    client = TelegramClient(session_name, api_id, api_hash)
    client.start()
    logger.print("Fetching channel list...", section_name="list_channels", level="info")

    async def list_channels():
        async for dialog in client.iter_dialogs():
            entity = dialog.entity
            if isinstance(entity, Channel):
                channel_id = entity.id
                channel_name = getattr(
                    entity, "title", getattr(entity, "username", "Unknown")
                )
                is_active = not getattr(entity, "left", False)
                logger.print(
                    f"Channel ID: {channel_id}, Name: {channel_name}, Active: {is_active}",
                    section_name="list_channels",
                    level="info",
                )

    with client:
        client.loop.run_until_complete(list_channels())
except (ValueError, RuntimeError, OSError) as e:
    logger.print(f"Error: {e}", section_name="list_channels", level="error")
