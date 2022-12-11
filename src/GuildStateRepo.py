from collections import namedtuple


GuildState = namedtuple("GuildState", ["main_message_id"])

_repo = {}

def get_state(guild_id: int) -> GuildState | None:
    return _repo.get(guild_id)

def set_state(guild_id: int, state: GuildState):
    _repo[guild_id] = state

def delete_state(guild_id: int):
    del _repo[guild_id]
