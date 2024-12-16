from pathlib import Path
from discord import Color, Embed
from discord.ext.commands import Bot, CommandError, Context
from src.exceptions import DomainError


class Bebot(Bot):
    async def setup_hook(self):
        # Load cogs
        cogs_path = Path(__file__).parent.joinpath("cogs")
        print(f"Loading cogs at {cogs_path}.")
        for file in cogs_path.glob("*.py"):
            print(f"Loading {file.stem}.")
            await self.load_extension(f"src.cogs.{file.stem}")

        await self.tree.sync()

    async def on_ready(self):
        print(f"Bot running as {self.user}.")

    async def on_command_error(self, ctx: Context, error):
        message = self.error_message(error)

        embed = Embed(color=Color.red())
        embed.add_field(name="Error", value=message)

        await ctx.send(embed=embed, delete_after=5)

    def error_message(self, error: CommandError) -> str:
        error = getattr(error, "original", error)

        if not isinstance(error, DomainError):
            raise error

        return error.message
