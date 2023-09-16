from discord.ext.commands import Context
from discord.ext.commands.cog import Cog
from src.bebot import Bebot


class BaseCog(Cog):
    def __init__(self, bot: Bebot):
        self.bot = bot

    async def cog_before_invoke(self, ctx: Context):
        await ctx.message.add_reaction("\N{OK HAND SIGN}")
