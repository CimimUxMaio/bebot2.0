import discord
import os
import src.exceptions as exceptions

from dotenv import load_dotenv
from src.bebot import Bebot

# Load .env file
load_dotenv()

# Initialize Bot client
intents = discord.Intents.default()
intents.message_content = True
bot = Bebot(command_prefix=".", intents=intents)


@bot.event
async def on_command_error(ctx, error):
    await exceptions.exception_handler(ctx=ctx, exception=error)


# Run program
if __name__ == "__main__":
    TOKEN = os.environ["DISCORD_TOKEN"]
    bot.run(TOKEN)
