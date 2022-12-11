import src.GuildStateRepo as GuildStateRepo
import typing
import discord.utils as discord_utils

from discord import Guild, TextChannel
from discord.ext.commands import Bot
from src.GuildStateRepo import GuildState


class Bebot(Bot):
    MAIN_CHANNEL_NAME = "musiquita-jot"

    async def setup_hook(self):
        # Load cogs
        cogs = ["music"]
        for name in cogs:
            await self.load_extension(f"src.cogs.{name}")

    async def on_ready(self):
        await self.setup_guilds()
        print(f"Bot running as {self.user}.")

    async def setup_guilds(self):
        for guild in self.guilds:
            await self.setup_guild(guild)

    async def setup_guild(self, guild: Guild) -> GuildState:
        main_channel = discord_utils.get(guild.text_channels, name=self.MAIN_CHANNEL_NAME)
        if not main_channel:
            main_channel = await guild.create_text_channel("Musiquita Jot")

        main_message = await main_channel.send("Buenas!")
        state = GuildState(
            main_channel_id = main_channel.id,
            main_message_id = main_message.id
        )
        GuildStateRepo.set_state(guild.id, state)
        return state

    async def get_or_setup_main_channel(self, guild: Guild) -> TextChannel:
        state = GuildStateRepo.get_state(guild.id)
        if not state:
            state = await self.setup_guild(guild)

        channel = self.get_channel(state.main_channel_id)
        if not channel:
            state = await self.setup_guild(guild)
            channel = self.get_channel(state.main_channel_id)

        return typing.cast(TextChannel, channel)
        
