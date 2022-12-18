import src.guildstaterepo as GuildStateRepo

from discord import Guild, Message
from discord.ext.commands import Bot
from src.guildstaterepo import GuildState
from src.music.client import MusicClient


class Bebot(Bot):
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
        guild = message.guild
        if message.author != self.user and guild:
            guild_state = await GuildStateRepo.get(guild)
            main_message = guild_state.main_message
            if main_message != message and main_message.channel == message.channel:
                await message.delete(delay=3)

        return await super().on_message(message)

    async def on_guild_join(self, guild: Guild):
        await self.setup_guild(guild)

    async def on_guild_remove(self, guild: Guild):
        GuildStateRepo.delete(guild.id)

    async def setup_guilds(self):
        for guild in self.guilds:
            await self.setup_guild(guild)

    async def setup_guild(self, guild: Guild):
        main_message = await GuildStateRepo.setup_main_channel(guild)
        state = GuildState(main_message = main_message, music_client=MusicClient(bot=self, guild=guild))
        GuildStateRepo.store(guild.id, state)
