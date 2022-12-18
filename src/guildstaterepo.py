import src.exceptions as exceptions
import discord.utils as discord_utils
import src.strings as strings
import src.mainmsg as mainmsg

from discord.errors import NotFound
from dataclasses import dataclass
from discord import Guild, Message
from typing import Dict
from src.music.client import MusicClient


@dataclass
class GuildState:
    main_message: Message
    music_client: MusicClient


_repo: Dict[int, GuildState] = {}

def has_guild(guild_id: int) -> bool:
    return guild_id in _repo.keys()

async def setup_main_channel(guild: Guild) -> Message:
    # Create text channel if it does not exist
    main_channel = discord_utils.get(guild.text_channels, name = strings.MAIN_CHANNEL_NAME)
    if not main_channel:
        main_channel = await guild.create_text_channel(strings.MAIN_CHANNEL_NAME)

    # Remove all messages from the channel
    await main_channel.purge(limit=None)

    # Send main message
    return await mainmsg.send(main_channel)

def store(guild_id: int, state: GuildState):
    _repo[guild_id] = state

def delete(guild_id: int):
    del _repo[guild_id]

async def get(guild: Guild) -> GuildState:
    # Fail if guild was not setup
    if not has_guild(guild.id):
        raise exceptions.GuildStateNotSetup(guild.id)

    state = _repo[guild.id]
    try:
        # Fetch updated message
        updated_message = await state.main_message.fetch()
    except NotFound:
        # If message is not found, setup main channel
        updated_message = await setup_main_channel(guild)

    # Store updated message
    state.main_message = updated_message
    store(guild.id, state)

    return state


