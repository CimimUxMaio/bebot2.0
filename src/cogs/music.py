from discord.ext.commands import Context, command
from discord.ext.commands.cog import Cog
from src.bebot import Bebot


class MusicCog(Cog, name = "Music"):
    def __init__(self, bot: Bebot):
        self.bot = bot

    @command(aliases=["q", "p"], name="queue")
    async def queue(self, _: Context, *, search: str):
        print(search)


async def setup(bot: Bebot):
    await bot.add_cog(MusicCog(bot))
