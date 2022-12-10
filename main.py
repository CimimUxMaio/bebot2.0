import discord
import os
from dotenv import load_dotenv
from src.bebot import Bebot

# Load .env file
load_dotenv()

# Initialize Bot client
intents = discord.Intents.default()
intents.message_content = True
bot = Bebot(command_prefix=".", intents=intents)

# Run program
if __name__ == "__main__":
    TOKEN = os.environ["DISCORD_TOKEN"]
    bot.run(TOKEN)
