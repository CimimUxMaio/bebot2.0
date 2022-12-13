
class DomainException(Exception):
    def __init__(self, message):
        super().__init__(message)


def GuildStateNotSetup(guild_id):
    return DomainException(f"Guild state not found for {guild_id}")
    
