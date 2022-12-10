import discord
import os
import asyncio
from dotenv import load_dotenv
from src.bebot import Bebot

# Load .env file
load_dotenv()

# Initialize Bot client
intents = discord.Intents.default()
intents.message_content = True
bot = Bebot(command_prefix=".", intents=intents)

# Main program
async def main():
    TOKEN = os.environ["DISCORD_TOKEN"]
    async with bot:
        await bot.start(TOKEN, reconnect=True)

# Run program
if __name__ == "__main__":
    asyncio.run(main())
