import src.music.service as music_service
import src.exceptions as exceptions
import src.messages.queue as queuemsg
import os
import re

from src.cogs.base import BaseCog
from discord.ext.commands import Context, command
from discord import Attachment, Guild, Member, VoiceChannel
from typing import cast
from src.music.client import MusicClient
from src.bebot import Bebot
from src.utils import SuperContext


class MusicCog(BaseCog, name="Music"):
    def __init__(self, bot: Bebot):
        self.bot = bot

    @command(aliases=["p"], name="play", help="Queue the given song (or \",\" separated songs).")
    async def play(self, ctx: Context, *, searches: str | None = None):
        guild = cast(Guild, ctx.guild)
        attachments = ctx.message.attachments

        search_list = []
        if searches:
            if playlist_match := re.match(r"\[([\w\d\s_-]+)\]", searches):
                playlist_name = playlist_match.group(1)
                playlist = await self.find_playlist(guild, playlist_name)
                search_list = await self.read_playlist(playlist)

            else:  # Take song(s) from arguments
                search_list = searches.split(",")

        # Take song(s) from attachment file
        elif len(attachments) > 0:
            search_list = await self.read_playlist(attachments[0])

        if len(search_list) == 0:
            raise exceptions.NoSearchesProvided()

        music_client = self.get_music_client(ctx)
        voice_channel: VoiceChannel = ctx.author.voice.channel  # type: ignore
        await music_client.connect(voice_channel)

        async with ctx.typing():
            for search in search_list:
                song = await music_service.download_song(search)
                await music_client.queue(song)

    @command(aliases=["sk"], name="skip", help="Skips the current song.")
    async def skip(self, ctx: Context):
        self.get_music_client(ctx).skip_current_song()

    @command(aliases=["st"],
             name="stop",
             help="Stops / resumes the song that is currently playing.")
    async def stop(self, ctx: Context):
        self.get_music_client(ctx).toggle_pause_resume()

    @command(aliases=["l"], name="leave", help="Disconnects Bebot from the voice channel.")
    async def leave(self, ctx: Context):
        await self.get_music_client(ctx).disconnect()

    @command(aliases=["q"], name="queue", help="Show the current music queue.")
    async def queue(self, ctx: Context):
        music_client = self.get_music_client(ctx)
        await queuemsg.send(SuperContext(self.bot, ctx), music_client)

    @command(
        name="playlists", help="Shows all available playlist names from the playlists channel.")
    async def playlists(self, ctx: Context):
        playlists = await self.get_playlists(cast(Guild, ctx.guild))
        names = [os.path.splitext(playlist.filename)[0] for playlist in playlists]
        response_message = "\n".join([f"- {name}" for name in names])
        if len(playlists) == 0:
            response_message = " ".join([
                "No hay ninguna playlist en el canal de playlists, "
                "agregá una subiendo un archivo con el nombre de la playlist al canal de texto."
            ])
        await ctx.send(response_message)

    async def get_playlists(self, guild: Guild) -> list[Attachment]:
        playlists_channel = self.bot.get_playlists_channel(guild)
        if not playlists_channel:
            raise exceptions.PlaylistsChannelNotFound()

        playlists = [msg async for msg in playlists_channel.history(limit=200)
                     if len(msg.attachments) > 0]
        return [msg.attachments[0] for msg in playlists]

    async def find_playlist(self, guild: Guild, name: str) -> Attachment:
        available_playlists = await self.get_playlists(guild)
        find = next((playlist for playlist in available_playlists), None)
        if not find:
            raise exceptions.PlaylistNotFound(name)
        return find

    async def read_playlist(self, playlist: Attachment) -> list[str]:
        file_content = await playlist.read()
        # Remove windows \r characters.
        return file_content.decode("utf-8").replace("\r", "").split("\n")

    @ play.before_invoke
    @ skip.before_invoke
    @ stop.before_invoke
    @ leave.before_invoke
    async def check_voice_channel(self, ctx: Context):
        await SuperContext(self.bot, ctx).check_voice_channel()

    def get_music_client(self, ctx: Context) -> MusicClient:
        guild = cast(Guild, ctx.guild)
        state = self.bot.state_repo.get(guild.id)
        return state.music_client

    # Framework methods #

    def cog_check(self, ctx: Context) -> bool:
        if not ctx.guild:
            raise exceptions.NotAGuildMessage()

        if not isinstance(ctx.author, Member):
            raise exceptions.AuthorTypeIsNotMember()

        return True


async def setup(bot: Bebot):
    await bot.add_cog(MusicCog(bot))
