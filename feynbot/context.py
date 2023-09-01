"""Contains the `context` class, containing relevant information about any
command, event, or interaction.  Allowing for easy access for the user to code
without needing to know the specifics."""

import discord


class Context:
    """Contains relevant information about a command, event, or interaction and
    methods to interact with it."""

    def __init__(
        self,
        message: discord.Message,
        guild: discord.Guild,
        channel: discord.TextChannel,
        member: discord.Member,
        author: discord.User,
        roles: list[discord.Role],
        user: discord.User,
    ) -> None:
        """Initialize the context."""
        self.message = message
        self.guild = guild
        self.channel = channel
        self.member = member
        self.author = author
        self.roles = roles
        self.user = user

        # is DMs?
        # is command?
        # is event?
        # is admin?/owner
        # is bot?
        # time
        # get permissions
        # reply
        # react
        # delete
        # pin
        # edit
        # sendTo
