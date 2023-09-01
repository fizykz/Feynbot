"""Initializes the bot, creating it, passing configuration, and starting it."""

import pyjson5 as json

from feynbot.bot import Feynbot


# Load configuration
with open("config.json", encoding="utf-8") as file:
    config: dict = json.load(file)

with open("intents.json", encoding="utf-8") as file:
    config["intents"] = json.load(file)["intents"]

bot = Feynbot(**config)


# IMPLEMENT: Fatal Error handling
bot.run()
