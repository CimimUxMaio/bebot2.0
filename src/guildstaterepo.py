from collections import namedtuple


GuildState = namedtuple("GuildState", ["main_message_id"])

_repo = {}

def get(guild_id: int) -> GuildState | None:
    return _repo.get(guild_id)

def store(guild_id: int, state: GuildState):
    _repo[guild_id] = state

def delete(guild_id: int):
    del _repo[guild_id]
