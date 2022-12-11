from collections import namedtuple


GuildState = namedtuple("GuildState", ["main_channel_id", "main_message_id"])

_repo = {}

def get_state(guild_id: int) -> GuildState | None:
    return _repo.get(guild_id)

def set_state(guild_id: int, state: GuildState):
    _repo[guild_id] = state
