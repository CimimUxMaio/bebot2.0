import discord
import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

# Define bot intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=".", intents=intents)


@bot.event
async def on_ready():
    print(f"Bot running as {bot.user}.")


@bot.event
async def on_message(message):
    print(message)


# Run program
if __name__ == "__main__":
    TOKEN = os.environ["DISCORD_TOKEN"]
    bot.run(TOKEN)
