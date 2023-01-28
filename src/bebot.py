import discord.utils as discord_utils
import src.messages.mainmsg as mainmsg
import src.exceptions as exceptions
import src.strings as strings

from discord import Guild, Message, TextChannel
from discord.ext.commands import Bot
from src.guildstaterepo import GuildState, GuildStateRepo
from src.music.client import MusicClient


class Bebot(Bot):
    def __init__(self, *args, **kwargs):
        self.state_repo = GuildStateRepo(self)
        super().__init__(*args, **kwargs)

    async def setup_hook(self):
        # Load cogs
        cogs = ["music"]
        for name in cogs:
            await self.load_extension(f"src.cogs.{name}")

    async def on_ready(self):
        # Initialize state for all guilds
        await self.setup_guilds()
        print(f"Bot running as {self.user}.")

    async def on_message(self, message: Message):
        # If message was sent through the main channel,
        # delete it after a few seconds
        channel = message.channel
        if (
            message.author != self.user
            and isinstance(channel, TextChannel)
            and channel.name == strings.MAIN_CHANNEL_NAME
        ):
            await message.delete(delay=3)

        return await super().on_message(message)

    async def on_guild_join(self, guild: Guild):
        await self.setup_guild(guild)

    async def on_guild_remove(self, guild: Guild):
        self.state_repo.delete(guild.id)

    async def setup_guilds(self):
        for guild in self.guilds:
            await self.setup_guild(guild)

    async def setup_guild(self, guild: Guild):
        main_message = await self.setup_main_channel(guild)
        state = GuildState(
            main_message_id=main_message.id,
            music_client=MusicClient(bot=self, guild_id=guild.id),
        )
        self.state_repo.store(guild.id, state)

    async def setup_main_channel(self, guild: Guild) -> Message:
        # Create text channel if it does not exist
        main_channel = discord_utils.get(
            guild.text_channels, name=strings.MAIN_CHANNEL_NAME
        )
        if not main_channel:
            main_channel = await guild.create_text_channel(strings.MAIN_CHANNEL_NAME)

        # Remove all messages from the channel
        await main_channel.purge(limit=None)

        # Send main message
        return await mainmsg.send(self, main_channel)

    async def fetch_or_set_main_message(self, guild_id: int) -> Message:
        main_message = await self.state_repo.fetch_main_message(guild_id)
        if main_message:
            return main_message

        guild = self.get_guild(guild_id)
        if not guild:
            raise exceptions.GuildNotFound(guild_id)

        return await self.setup_main_channel(guild)
