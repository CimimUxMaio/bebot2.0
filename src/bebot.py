import src.guildstaterepo as GuildStateRepo
import discord.utils as discord_utils
import src.mainmsg as mainmsg
import src.strings as strings

from discord import Guild
from discord.ext.commands import Bot
from src.guildstaterepo import GuildState


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

    async def on_guild_join(self, guild: Guild):
        await self.setup_guild(guild)

    async def on_guild_remove(self, guild: Guild):
        GuildStateRepo.delete(guild.id)

    async def setup_guilds(self):
        for guild in self.guilds:
            await self.setup_guild(guild)

    async def setup_guild(self, guild: Guild):
        # Create text channel if it does not exist
        main_channel = discord_utils.get(guild.text_channels, name=strings.MAIN_CHANNEL_NAME)
        if not main_channel:
            main_channel = await guild.create_text_channel(strings.MAIN_CHANNEL_NAME)

        # Remove all messages from the channel
        await main_channel.purge(limit=None)

        # Send main message and set the guild's state
        main_message = await mainmsg.send(main_channel)
        state = GuildState(main_message_id = main_message.id)
        GuildStateRepo.store(guild.id, state)
