from src.exceptions.domainerror import DomainError


def NoSearchesProvided() -> DomainError:
    message = " ".join([
        "No songs where provided.",
        "Please provide them as a \",\" separated list",
        "or in a text file attachment separating songs line by line."
    ])
    return DomainError(message)


def SongNotFound(search: str) -> DomainError:
    return DomainError(f"Couldn't find a song with name: {search}")


def UnexpectedSongResponse(search: str) -> DomainError:
    return DomainError(f"The search for {search} returned an unexpected result")


def VoiceClientNotSet() -> DomainError:
    return DomainError("Voice client not set")


def UserNotConnectedToVoiceChannel() -> DomainError:
    return DomainError("User not connected to a voice channel")


def BotConnectedToAnotherChannel() -> DomainError:
    return DomainError("Bebot is currently connected to another channel")


def PlaylistNotFound(playlist_name: str) -> DomainError:
    return DomainError(f"Playlist with name: {playlist_name} not found")
