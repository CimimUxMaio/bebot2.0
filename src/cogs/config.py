from typing import cast
import src.exceptions as exceptions

from src.cogs.base import BaseCog
from discord.ext.commands import Context, command
from discord import Member, Guild
from src.bebot import Bebot


class ConfigCog(BaseCog, name="Config"):
    def __init__(self, bot: Bebot):
        self.bot = bot

    @command(name="config:setup", help="")
    async def setup_guild(self, ctx: Context):
        guild = cast(Guild, ctx.guild)
        await self.bot.setup_guild(guild)

    @command(name="config:playlists:clean", help="")
    async def clean_playlists_channel(self, ctx: Context):
        guild = cast(Guild, ctx.guild)
        playlists_channel = self.bot.get_playlists_channel(guild)
        if not playlists_channel:
            raise exceptions.PlaylistsChannelNotFound()
        await self.bot.clean_playlists_channel(playlists_channel)

    # Framework methods #

    def cog_check(self, ctx: Context) -> bool:
        if not ctx.guild:
            raise exceptions.NotAGuildMessage()

        if not isinstance(ctx.author, Member):
            raise exceptions.AuthorTypeIsNotMember()

        return True


async def setup(bot: Bebot):
    await bot.add_cog(ConfigCog(bot))
