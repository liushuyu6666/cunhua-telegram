from telethon.tl import types


class DialogType:
    PRIVATE_CHAT = "private chat"
    GROUP = "group"
    CHANNEL = "channel"
    UNKNOWN = "unknown"

    @staticmethod
    def get_type(entity):
        if isinstance(entity, types.User):
            return DialogType.PRIVATE_CHAT
        elif isinstance(entity, types.Chat):
            return DialogType.GROUP
        elif isinstance(entity, types.Channel):
            if entity.megagroup:
                return DialogType.GROUP
            return DialogType.CHANNEL
        return DialogType.UNKNOWN
