from src.exceptions.domainerror import DomainError


def AuthorTypeIsNotMember() -> DomainError:
    return DomainError("Author is not a guild member")


def NotAGuildMessage() -> DomainError:
    return DomainError("DM channel commands not supported")
