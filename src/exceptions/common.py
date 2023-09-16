from src.exceptions.domainerror import DomainError


def AuthorTypeIsNotMember() -> DomainError:
    return DomainError("Author is not a guild member")


def NotAGuildMessage() -> DomainError:
    return DomainError("DM channel commands not supported")


def GuildNotFound(guild_id: int) -> DomainError:
    return DomainError(f"Guild with id: {guild_id} not found")


def GuildStateNotSetup(guild_id: int) -> DomainError:
    return DomainError(f"Guild state not found for {guild_id}")


def PlaylistsChannelNotFound() -> DomainError:
    return DomainError("Playlists channel not found. Please run .config:setup to setup the server")


def MainMessageNotFound() -> DomainError:
    return DomainError("Main message not found. Please run .config:setup to setup the server")
