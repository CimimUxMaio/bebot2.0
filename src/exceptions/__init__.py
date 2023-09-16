from src.exceptions.music import *
from src.exceptions.common import *

from src.exceptions.domainerror import DomainError
from discord import Color, Embed


async def exception_handler(ctx, exception: Exception):
    if not isinstance(exception, DomainError):
        raise exception

    embed = Embed(color=Color.red())
    embed.add_field(name="Error", value=exception.message)
    await ctx.send_message(embed=embed, delete_after=5)
