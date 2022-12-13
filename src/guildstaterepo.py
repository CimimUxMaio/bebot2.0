import src.exceptions as exceptions

from collections import namedtuple


GuildState = namedtuple("GuildState", ["main_message_id"])

_repo = {}

def has_guild(guild_id: int) -> bool:
    return guild_id in _repo.keys()

def get(guild_id: int) -> GuildState:
    if not has_guild(guild_id):
        raise exceptions.GuildStateNotSetup(guild_id)

    return _repo[guild_id]

def store(guild_id: int, state: GuildState):
    _repo[guild_id] = state

def delete(guild_id: int):
    del _repo[guild_id]
