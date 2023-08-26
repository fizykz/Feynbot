"""Initializes the bot, creating it, passing configuration, and starting it."""

import pyjson5 as json

from source.feynbot import Feynbot

# Load configuration
with open("config.json", encoding="utf-8") as file:
    config: dict = json.load(file)  # pylint: disable=no-member

bot = Feynbot(**config)
# TODO: Error handling
bot.run()
