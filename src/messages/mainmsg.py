import discord
import discord.ui as ui
import src.strings as strings
import src.messages.pages as pages 
import src.utils as utils

from discord import Embed, Interaction, Message, TextChannel
from src.guildstaterepo import GuildState
from src.music.client import MusicClient, MusicState
from typing import cast


def MainEmbed(music_state: MusicState | None = None) -> Embed:
    embed = Embed(color=discord.Color.random())

    if not music_state or not music_state.current_song:
        current_msg = strings.NOTHING_PLAYING
    else:
        current_msg = music_state.current_song.title

    embed.add_field(name = strings.NOW_PLAYING, value = current_msg, inline=False)
    embed.set_image(url = "attachment://status.gif")
    return embed


def no_response(func):
    async def wrapper(ref, interaction: Interaction, button: ui.Button):
        await func(ref, interaction, button)
        await interaction.response.edit_message()
    return wrapper

def with_music_client(func):
    async def wrapper(ref, interaction: Interaction, button: ui.Button, **kwargs):
        state: GuildState = ref.bot.state_repo.get(cast(int, interaction.guild_id))
        kwargs["music_client"] = state.music_client
        return await func(ref, interaction, button, **kwargs)
    return wrapper

def when_condition(func, condition):
    async def wrapper(*args, **kwargs):
        if not condition(*args, **kwargs):
            return 
        return await func(*args, **kwargs)
    return wrapper

def when_connected(func):
    def condition(ref, *_, music_client: MusicClient):
        return music_client.is_connected()
    return with_music_client(when_condition((func), condition))


class MainView(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @ui.button(label=strings.PLAY_STOP_BUTTON_LABEL)  # type: ignore
    @no_response
    @when_connected
    async def stop_resume(self, *_, music_client: MusicClient):
        music_client.toggle_pause_resume()

    @ui.button(label=strings.NEXT_BUTTON_LABEL)  # type: ignore
    @no_response
    @when_connected
    async def next(self, *_, music_client: MusicClient):
        music_client.skip_current_song()

    @ui.button(label=strings.QUEUE_BUTTON_LABEL)  # type: ignore
    @with_music_client
    async def queue(self, interaction: Interaction, _: ui.Button, music_client: MusicClient):
        current_song = music_client.current_song
        queue_pages = [Embed(description = strings.QUEUE_NOTHING_PLAYING)]
        if current_song:
            current_title = current_song.title
            titles = [f"{pos}. {song.title}" for pos, song in enumerate(music_client.queue(), start=1)]
            queue_pages = self.generate_queue_pages(current_title, titles)

        await pages.send(interaction, queue_pages)

    @ui.button(label=strings.LEAVE_BUTTON_LABEL)  # type: ignore
    @no_response
    @with_music_client
    async def leave(self, *_, music_client: MusicClient):
        await music_client.disconnect()

    def get_music_client(self, guild_id: int) -> MusicClient:
        state: GuildState = self.bot.state_repo.get(guild_id)
        return state.music_client

    def queue_group_page(self, current, titles) -> Embed:
        embed = Embed(title=strings.QUEUE_CURRENT % f"\"{current}\"")
        embed.add_field(
            name  = "\a",
            value = "\n".join(titles)
        )
        return embed

    def generate_queue_pages(self, current_title: str, titles: list[str], page_size: int = 5) -> list[Embed]:
        if len(titles) == 0:
            return [Embed(title=current_title)]

        title_groups = utils.group(titles, page_size)
        return [self.queue_group_page(current_title, group) for group in title_groups]


async def send(bot, channel: TextChannel) -> Message:
    profile_pic = discord.File("./assets/music_playing.gif", filename="status.gif")
    return await channel.send(embed=MainEmbed(), view=MainView(bot), files=[profile_pic])

async def update(message: Message, state: MusicState) -> Message:
    profile_pic = discord.File("./assets/music_playing.gif", filename="status.gif")
    return await message.edit(embed=MainEmbed(state), attachments=[profile_pic])

