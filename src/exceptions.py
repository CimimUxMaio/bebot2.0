
class DomainException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


def GuildStateNotSetup(guild_id: int) -> DomainException:
    return DomainException(f"Guild state not found for {guild_id}")

def SongNotFound(search: str) -> DomainException:
    return DomainException(f"Couldn't find a song with name: {search}")
    
def UnexpectedSongResponse(search: str) -> DomainException:
    return DomainException(f"The search for {search} returned an unexpected result")

def VoiceClientNotSet():
    return DomainException("Voice client not set")

def NotAGuildMessage():
    return DomainException("DM channel commands not supported")

def UserNotConnectedToVoiceChannel():
    return DomainException("User not connected to a voice channel")
    
def BotConnectedToAnotherChannel():
    return DomainException("Bebot is currently connected to another channel")

def AuthorTypeIsNotMember():
    return DomainException("Author is not a guild member")
