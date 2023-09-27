import discord
import discord.ui as ui
import src.strings as strings
import src.messages.queue as queuemsg
import src.exceptions as exceptions

from discord import Embed, Interaction, Message, TextChannel
from src.guildstaterepo import GuildState
from src.music.client import MusicClient, MusicState
from typing import Any, cast
from src.utils import SuperContext


def MainEmbed(music_state: MusicState | None = None) -> Embed:
    embed = Embed(color=discord.Color.random())

    if not music_state or not music_state.current_song:
        current_msg = strings.NOTHING_PLAYING
    else:
        current_msg = music_state.current_song.title

    embed.add_field(name=strings.NOW_PLAYING, value=current_msg, inline=False)
    embed.set_image(url="attachment://status.gif")
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


def check_voice_channel(func):
    async def wrapper(ref, interaction: Interaction, button: ui.Button, **kwargs):
        await SuperContext(ref.bot, interaction).check_voice_channel()
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
        from src.bebot import Bebot  # Circular import
        self.bot: Bebot = bot

    @ui.button(label=strings.PLAY_STOP_BUTTON_LABEL)  # type: ignore
    @no_response
    @when_connected
    @check_voice_channel
    async def stop_resume(self, *_, music_client: MusicClient):
        music_client.toggle_pause_resume()

    @ui.button(label=strings.NEXT_BUTTON_LABEL)  # type: ignore
    @no_response
    @when_connected
    @check_voice_channel
    async def next(self, *_, music_client: MusicClient):
        music_client.skip_current_song()

    @ui.button(label=strings.QUEUE_BUTTON_LABEL)  # type: ignore
    @with_music_client
    async def queue(
        self, interaction: Interaction, _: ui.Button, music_client: MusicClient
    ):
        await queuemsg.send(SuperContext(self.bot, interaction), music_client)

    @ui.button(label=strings.LEAVE_BUTTON_LABEL)  # type: ignore
    @no_response
    @with_music_client
    @check_voice_channel
    async def leave(self, *_, music_client: MusicClient):
        await music_client.disconnect()

    def get_music_client(self, guild_id: int) -> MusicClient:
        state: GuildState = self.bot.state_repo.get(guild_id)
        return state.music_client

    async def on_error(self, interaction: Interaction, error: Exception, _: ui.Item[Any], /):
        await exceptions.exception_handler(ctx=SuperContext(self.bot, interaction), exception=error)


async def send(bot, channel: TextChannel) -> Message:
    profile_pic = discord.File("./assets/music_playing.gif", filename="status.gif")
    return await channel.send(
        embed=MainEmbed(), view=MainView(bot), files=[profile_pic]
    )


async def update(message: Message, state: MusicState) -> Message:
    profile_pic = discord.File("./assets/music_playing.gif", filename="status.gif")
    return await message.edit(embed=MainEmbed(state), attachments=[profile_pic])
