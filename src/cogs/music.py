import src.music.service as music_service
import src.exceptions as exceptions
import src.messages.queue as queuemsg

from discord.ext.commands import Context, command
from discord.ext.commands.cog import Cog
from discord import Guild, Member, VoiceChannel
from typing import cast
from src.music.client import MusicClient
from src.bebot import Bebot
from src.utils import SuperContext


class MusicCog(Cog, name="Music"):
    def __init__(self, bot: Bebot):
        self.bot = bot

    @command(aliases=["p"], name="play", help="Queue the given song (or \",\" separated songs).")
    async def play(self, ctx: Context, *, searches: str | None = None):
        attachments = ctx.message.attachments
        if searches and len(searches.strip()) != 0:  # Take song(s) from arguments
            search_list = searches.split(",")

        # Take song(s) from attachment file
        elif len(attachments) > 0:
            file_content = await attachments[0].read()
            print(file_content)
            # Remove windows \r characters.
            search_list = file_content.decode("utf-8").replace("\r", "").split("\n")
            print(search_list)

        else:
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

    @play.before_invoke
    @skip.before_invoke
    @stop.before_invoke
    @leave.before_invoke
    async def check_voice_channel(self, ctx: Context):
        await SuperContext(self.bot, ctx).check_voice_channel()
        # author = cast(Member, ctx.author)
        # if not author.voice or not author.voice.channel:
        #     raise exceptions.UserNotConnectedToVoiceChannel()

        # if ctx.voice_client and ctx.voice_client.channel != author.voice.channel:
        #     raise exceptions.BotConnectedToAnotherChannel()

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

    async def cog_after_invoke(self, ctx: Context):
        await ctx.message.add_reaction("\N{OK HAND SIGN}")


async def setup(bot: Bebot):
    await bot.add_cog(MusicCog(bot))
