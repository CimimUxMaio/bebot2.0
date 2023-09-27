import src.messages.pages as pagesmsg
import src.strings as strings
import src.utils as utils

from discord import Embed


def playlist_group_page(playlists) -> Embed:
    embed = Embed(title="Available Playlists")
    # ** ** is a hack to get an empty field name.
    embed.add_field(name="** **", value="\n".join([f"- {name}" for name in playlists]))
    return embed


def generate_playlists_pages(playlists: list[str], page_size: int = 5) -> list[Embed]:
    page_groups = utils.group(playlists, page_size)
    return [playlist_group_page(group) for group in page_groups]


async def send(ctx: utils.SuperContext, playlists: list[str]):
    playlists_pages = [Embed(description=strings.NO_PLAYLISTS_AVAILABLE)]
    if len(playlists) > 0:
        playlists_pages = generate_playlists_pages(playlists)
    await pagesmsg.send(ctx, playlists_pages)
