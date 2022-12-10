import discord
import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

# Define bot intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=".", intents=intents)


# Base events
@bot.event
async def on_ready():
    # Load cogs
    cogs = ["music"]
    for name in cogs:
        await bot.load_extension(f"src.cogs.{name}")

    print(f"Bot running as {bot.user}.")


# Run program
if __name__ == "__main__":
    TOKEN = os.environ["DISCORD_TOKEN"]
    bot.run(TOKEN)
