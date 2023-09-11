import src.messages.pages as pagesmsg
import src.strings as strings
import src.utils as utils

from discord import Embed
from src.music.client import MusicClient


def queue_group_page(current, titles) -> Embed:
    embed = Embed(title=strings.QUEUE_CURRENT % f'"{current}"')
    embed.add_field(name="\a", value="\n".join(titles))
    return embed


def generate_queue_pages(current_title: str, titles: list[str], page_size: int = 5
                         ) -> list[Embed]:
    if len(titles) == 0:
        return [Embed(title=current_title)]

    title_groups = utils.group(titles, page_size)
    return [queue_group_page(current_title, group) for group in title_groups]


async def send(ctx: utils.SuperContext, music_client: MusicClient):
    current_song = music_client.current_song
    queue_pages = [Embed(description=strings.QUEUE_NOTHING_PLAYING)]
    if current_song:
        current_title = current_song.title
        titles = [
            f"{pos}. {song.title}"
            for pos, song in enumerate(music_client.queue(), start=1)
        ]
        queue_pages = generate_queue_pages(current_title, titles)
    await pagesmsg.send(ctx, queue_pages)
