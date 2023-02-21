from typing import TypeVar
from discord import Embed, Interaction
from discord.ext.commands import Context
from discord.ui import View


T = TypeVar("T")


def group(_list: list[T], group_size: int) -> list[list[T]]:
    return [_list[i: i + group_size] for i in range(0, len(_list), group_size)]


class SuperContext:
    def __init__(self, ctx: Interaction | Context):
        self._ctx = ctx

    async def send_message(self, content: str | None = None, *,
                           embed: Embed | None = None,
                           view: View | None = None,
                           delete_after: float | None = None):
        if isinstance(self._ctx, Context):
            return await self._ctx.send(
                content=content,
                embed=embed,
                view=view,
                delete_after=delete_after
            )
        else:  # Is Interaction
            if not embed:
                embed = Embed()
            if not view:
                view = View()

            return await self._ctx.response.send_message(
                content=content,
                embed=embed,
                view=view,
                delete_after=delete_after
            )
