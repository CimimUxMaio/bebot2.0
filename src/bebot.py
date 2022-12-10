from discord.ext.commands import Bot


class Bebot(Bot):
    async def setup_hook(self):
        # Load cogs
        cogs = ["music"]
        for name in cogs:
            await self.load_extension(f"src.cogs.{name}")

    async def on_ready(self):
        print(f"Bot running as {self.user}.")
