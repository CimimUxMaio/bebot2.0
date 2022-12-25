import discord
import discord.ui as ui

from discord import Embed, Interaction
from discord.ext.commands import Context


class PagesView(ui.View):
    def __init__(self, pages: list[Embed], current: int = 0):
        super().__init__()
        self._current_page = current
        self.pages = pages

    @ui.button(emoji="⬅️")
    async def previous(self, interaction: Interaction, _: ui.Button):
        self._current_page = max(self._current_page - 1, 0)
        await self.edit_page_response(interaction)

    @ui.button(emoji="➡️")
    async def next(self, interaction: Interaction, _: ui.Button):
        self._current_page = min(self._current_page + 1, len(self.pages) - 1)
        await self.edit_page_response(interaction)

    def current_page(self) -> Embed:
        return self.pages[self._current_page]

    async def edit_page_response(self, interaction: Interaction):
        await interaction.response.edit_message(embed=self.current_page())


def format_page(page: Embed, n: int, page_amount: int) -> Embed:
    page.color = discord.Color.random()
    page.set_footer(text="Page %s/%s" % (n, page_amount))
    return page

async def send(ctx: Context | Interaction, pages: list[Embed]):
    page_amount = len(pages)
    pages = [format_page(p, n, page_amount) for n, p in enumerate(pages, start=1)]

    current = pages[0]
    view = PagesView(pages, 0)
    if isinstance(ctx, Context):
        message = await ctx.send(embed=current, view=view)
    else:  # Is Interaction
        await ctx.response.send_message(embed=current, view=view)
        message = await ctx.original_response()

    await message.delete(delay=30)


