"""
This script lists all dialogs (private chats, groups, channels) the user account has access to, including ID, name, type, and whether the dialog is active.
Run this file from the terminal after generating your session file.
"""

import os
import sys
from datetime import datetime, timezone

import bson
from dotenv import load_dotenv
from pymongo import MongoClient
from telethon import TelegramClient

from tgtypes.dialog import DialogType
from utils.logger import Logger

load_dotenv()

logger = Logger(visible_level="info")

api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
phone = os.getenv("PHONE")
session_name = os.getenv("SESSION_NAME")
mongo_uri = os.getenv("MONGO_URI")
mongo_db = os.getenv("MONGO_DB", "cunhua-telegram")
dialogs_collection = os.getenv("DIALOGS_COLLECTION", "dialogs")

if not all([api_id, api_hash, phone, session_name, mongo_uri]):
    logger.print(
        "API_ID, API_HASH, PHONE, SESSION_NAME, and/or MONGO_URI not found. Please set them in your .env file.",
        section_name="list_dialogs",
        level="error",
    )
    sys.exit(1)


def get_mongo_collection():
    mongo_client = MongoClient(mongo_uri)
    db = mongo_client[mongo_db]
    return db[dialogs_collection]


def fetch_cached_dialogs(collection):
    return list(collection.find({}, projection={"_id": 0}))


def cache_dialogs(collection, dialogs):
    collection.delete_many({})
    if dialogs:
        for dialog in dialogs:
            dialog.pop("_id", None)
            dialog["id"] = bson.Int64(dialog["id"])
        collection.insert_many(dialogs)


def get_dialog_data(entity):
    dialog_id = entity.id
    name = getattr(
        entity,
        "title",
        getattr(entity, "username", getattr(entity, "first_name", "Unknown")),
    )
    dialog_type = DialogType.get_type(entity)
    is_active = not getattr(entity, "left", False)
    now = datetime.now(timezone.utc)
    return {
        "id": dialog_id,
        "name": name,
        "type": dialog_type,
        "is_active": is_active,
        "created_at": now,
        "updated_at": now,
    }


def main(update=False):
    collection = get_mongo_collection()
    cached_dialogs = fetch_cached_dialogs(collection)
    if cached_dialogs and not update:
        logger.print(
            f"Loaded {len(cached_dialogs)} dialogs from cache.",
            section_name="list_dialogs",
            level="info",
        )
        for dialog in cached_dialogs:
            logger.print(
                f"ID: {dialog.get('id')}, Name: {dialog.get('name')}, Type: {dialog.get('type')}, Active: {dialog.get('is_active')}",
                section_name="list_dialogs",
                level="info",
            )
        return

    try:
        client = TelegramClient(session_name, api_id, api_hash)
        client.start()
        logger.print(
            "Fetching dialog list from Telegram...",
            section_name="list_dialogs",
            level="info",
        )

        async def list_dialogs():
            dialogs = []
            async for dialog in client.iter_dialogs():
                entity = dialog.entity
                dialog_data = get_dialog_data(entity)
                dialogs.append(dialog_data)
                logger.print(
                    f"ID: {dialog_data['id']}, Name: {dialog_data['name']}, Type: {dialog_data['type']}, Active: {dialog_data['is_active']}",
                    section_name="list_dialogs",
                    level="info",
                )
            cache_dialogs(collection, dialogs)

        with client:
            client.loop.run_until_complete(list_dialogs())
    except (ValueError, RuntimeError, OSError) as e:
        logger.print(f"Error: {e}", section_name="list_dialogs", level="error")


if __name__ == "__main__":
    update_flag = "--update" in sys.argv
    main(update=update_flag)
