import src.GuildStateRepo as GuildStateRepo
import discord.utils as discord_utils
import src.mainmsg as mainmsg

from discord import Guild
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
        # Initialize state for all guilds
        await self.setup_guilds()
        print(f"Bot running as {self.user}.")

    async def on_guild_join(self, guild: Guild):
        await self.setup_guild(guild)

    async def on_guild_remove(self, guild: Guild):
        GuildStateRepo.delete_state(guild.id)
        
    # async def on_reaction_add(self, reaction: Reaction, _: User):
    #     message = reaction.message
    #     guild = message.guild

    #     if guild:
    #         state = GuildStateRepo.get_state(guild.id)
    #         if state and state.main_message_id == message.id:
    #             # Is a main message reaction
    #             print("Reacted to main message")

    async def setup_guilds(self):
        for guild in self.guilds:
            await self.setup_guild(guild)

    async def setup_guild(self, guild: Guild):
        # Create text channel if it does not exist
        main_channel = discord_utils.get(guild.text_channels, name=self.MAIN_CHANNEL_NAME)
        if not main_channel:
            main_channel = await guild.create_text_channel(self.MAIN_CHANNEL_NAME)

        # Remove all messages from the channel
        await main_channel.purge(limit=None)

        # Send main message and set the guild's state
        main_message = await mainmsg.send(main_channel)
        state = GuildState(main_message_id = main_message.id)
        GuildStateRepo.set_state(guild.id, state)
