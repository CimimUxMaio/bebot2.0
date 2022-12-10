from discord.ext.commands import Context, command, Bot
from discord.ext.commands.cog import Cog


class MusicCog(Cog, name = "Music"):
    def __init__(self, bot: Bot):
        self.bot = bot

    @command(aliases=["q", "p"], name="queue")
    async def queue(self, _: Context, *, search: str):
        print(search)


async def setup(bot: Bot):
    await bot.add_cog(MusicCog(bot))
