import src.exceptions as exceptions
import discord.utils as discord_utils
import src.strings as strings

from discord.errors import NotFound
from dataclasses import dataclass
from discord import Message
from discord.ext.commands import Bot
from typing import Dict
from src.music.client import MusicClient


@dataclass
class GuildState:
    main_message_id: int
    music_client: MusicClient


class GuildStateRepo:
    def __init__(self, bot: Bot):
        self.bot: Bot = bot
        self._repo: Dict[int, GuildState] = {}

    def contains(self, guild_id: int) -> bool:
        return guild_id in self._repo.keys()

    def store(self, guild_id: int, state: GuildState):
        self._repo[guild_id] = state

    def delete(self, guild_id: int):
        del self._repo[guild_id]

    def get(self, guild_id: int) -> GuildState:
        # Fail if guild was not setup
        if not self.contains(guild_id):
            raise exceptions.GuildStateNotSetup(guild_id)

        return self._repo[guild_id]

    def get_music_client(self, guild_id) -> MusicClient:
        return self.get(guild_id).music_client

    async def fetch_main_message(self, guild_id) -> Message | None:
        main_message_id = self.get(guild_id).main_message_id
        guild = self.bot.get_guild(guild_id)

        if not guild:
            return None

        main_channel = discord_utils.get(
            guild.text_channels, name=strings.MAIN_CHANNEL_NAME
        )

        if not main_channel:
            return None

        try:
            return await main_channel.fetch_message(main_message_id)
        except NotFound:
            return None
