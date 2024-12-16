import src.exceptions as exceptions
import emoji

from discord import Member
from discord.ext.commands import Context
from discord.ext.commands.cog import Cog

from src.bebot import Bebot


class BaseCog(Cog):
    def __init__(self, bot: Bebot):
        self.bot = bot

    async def cog_before_invoke(self, ctx: Context):
        return await ctx.message.add_reaction(
            emoji.emojize(":ok_hand:", language="alias")
        )

    def cog_check(self, ctx: Context) -> bool:
        # Only accept guild messages
        if ctx.guild is None:
            raise exceptions.NotAGuildMessage()

        # Only accept Member authors
        if not isinstance(ctx.author, Member):
            raise exceptions.AuthorTypeIsNotMember()

        return True
