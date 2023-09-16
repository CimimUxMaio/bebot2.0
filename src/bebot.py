import discord.utils as discord_utils
import src.messages.mainmsg as mainmsg
import src.exceptions as exceptions
import src.strings as strings

from discord import CategoryChannel, Guild, Message, TextChannel
from discord.ext.commands import Bot
from src.guildstaterepo import GuildState, GuildStateRepo
from src.music.client import MusicClient
from src.utils import SuperContext


class Bebot(Bot):
    def __init__(self, *args, **kwargs):
        self.state_repo = GuildStateRepo(self)
        super().__init__(*args, **kwargs)

    async def setup_hook(self):
        # Load cogs
        cogs = ["music", "config"]
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
        await self.state_repo.delete(guild.id)

    async def setup_guilds(self):
        for guild in self.guilds:
            await self.setup_guild(guild)

    async def setup_guild(self, guild: Guild) -> Message:
        # Delete old state if any
        await self.state_repo.delete(guild.id)

        main_category = await self.get_or_create_main_category(guild)
        main_channel = await self.get_or_create_main_channel(guild, main_category)
        main_message = await self.create_main_message(main_channel)

        playlists_channel = await self.get_or_create_playlists_channel(guild, main_category)
        await self.clean_playlists_channel(playlists_channel)

        # Store new guild state on guild repository
        state = GuildState(
            main_message_id=main_message.id,
            music_client=MusicClient(bot=self, guild_id=guild.id)
        )

        self.state_repo.store(guild.id, state)
        return main_message

    async def get_or_create_main_category(self, guild: Guild) -> CategoryChannel:
        # Create category if it does not exist
        category = discord_utils.get(guild.categories, name=strings.MAIN_CATEGORY_NAME)
        if not category:
            category = await guild.create_category(strings.MAIN_CATEGORY_NAME, position=0)
        return category

    def get_main_channel(self, guild: Guild) -> TextChannel | None:
        return discord_utils.get(guild.text_channels, name=strings.MAIN_CHANNEL_NAME)

    async def get_or_create_main_channel(
            self, guild: Guild, category: CategoryChannel) -> TextChannel:
        # Create text channel if it does not exist
        channel = self.get_main_channel(guild)
        if not channel:
            channel = await guild.create_text_channel(strings.MAIN_CHANNEL_NAME, category=category)
        return channel

    def get_playlists_channel(self, guild: Guild) -> TextChannel | None:
        return discord_utils.get(guild.text_channels, name=strings.PLAYLISTS_CHANNEL_NAME)

    async def clean_playlists_channel(self, playlists_channel: TextChannel):
        def is_valid_playlist(message: Message) -> bool:
            return len(message.attachments) == 0

        # Remove all invalid playlist message
        await playlists_channel.purge(limit=200, check=is_valid_playlist)

    async def get_or_create_playlists_channel(
            self, guild: Guild, category: CategoryChannel) -> TextChannel:
        playlist_channel = self.get_playlists_channel(guild)

        # Create text channel if it does not exist
        if not playlist_channel:
            playlist_channel = await guild.create_text_channel(
                strings.PLAYLISTS_CHANNEL_NAME, category=category
            )
        return playlist_channel

    async def get_main_message(self, guild: Guild) -> Message | None:
        return await self.state_repo.fetch_main_message(guild.id)

    async def create_main_message(self, main_channel: TextChannel) -> Message:
        # Remove all messages from the channel
        await main_channel.purge(limit=200)

        # Send main message
        return await mainmsg.send(self, main_channel)

    # async def get_or_create_main_message(self, guild: Guild) -> Message:
    #     # Fetch main message from state repo
    #     main_message = await self.state_repo.fetch_main_message(guild.id)
    #     if main_message:
    #         return main_message

    #     return await self.setup_guild(guild)

    def find_guild(self, guild_id: int) -> Guild:
        guild = self.get_guild(guild_id)
        if not guild:
            raise exceptions.GuildNotFound(guild_id)
        return guild

    async def on_command_error(self, ctx, error):
        await exceptions.exception_handler(ctx=SuperContext(self, ctx), exception=error)
