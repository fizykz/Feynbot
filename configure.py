"""Prompts the user for the necessary information to change or create
`config.json`.  This file contains the keys, IDs, and other settings for the
bot."""

import pyjson5 as json
from typing import Any

config: dict[str, Any] = {}

# Settings:
# Emoji servers (Automatically adds all emojis to the bot's cache for lookup)
