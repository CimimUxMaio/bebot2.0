from discord.ext.commands import CommandError


class DomainError(CommandError):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)
