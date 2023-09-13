from discord import Color, Embed
from discord.ext.commands import CommandError


class DomainException(CommandError):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


def GuildStateNotSetup(guild_id: int) -> DomainException:
    return DomainException(f"Guild state not found for {guild_id}")


def NoSearchesProvided() -> DomainException:
    message = " ".join([
        "No songs where provided.",
        "Please provide them as a \",\" separated list",
        "or in a text file attachment separating songs line by line."
    ])
    return DomainException(message)


def SongNotFound(search: str) -> DomainException:
    return DomainException(f"Couldn't find a song with name: {search}")


def UnexpectedSongResponse(search: str) -> DomainException:
    return DomainException(f"The search for {search} returned an unexpected result")


def VoiceClientNotSet() -> DomainException:
    return DomainException("Voice client not set")


def NotAGuildMessage() -> DomainException:
    return DomainException("DM channel commands not supported")


def UserNotConnectedToVoiceChannel() -> DomainException:
    return DomainException("User not connected to a voice channel")


def BotConnectedToAnotherChannel() -> DomainException:
    return DomainException("Bebot is currently connected to another channel")


def AuthorTypeIsNotMember() -> DomainException:
    return DomainException("Author is not a guild member")


def GuildNotFound(guild_id: int) -> DomainException:
    return DomainException(f"Guild with id: {guild_id} not found")


async def exception_handler(ctx, exception: Exception):
    if not isinstance(exception, DomainException):
        raise exception

    embed = Embed(color=Color.red())
    embed.add_field(name="Error", value=exception.message)
    await ctx.send_message(embed=embed, delete_after=5)
