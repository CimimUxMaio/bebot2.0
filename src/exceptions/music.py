import src.strings.exceptions as strings

from src.exceptions.domainerror import UserError


def SongNotFound(search: str) -> UserError:
    return UserError(strings.SONG_NOT_FOUND.format(search))


def UserNotConnectedToVoiceChannel() -> UserError:
    return UserError(strings.USER_NOT_CONNECTED_TO_VOICE_CHANNEL)


def BotConnectedToAnotherChannel() -> UserError:
    return UserError(strings.BEBOT_CONNECTED_TO_ANOTHER_CHANNEL)
