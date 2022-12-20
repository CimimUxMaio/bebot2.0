import src.music.service as music_service
import src.exceptions as exceptions

from discord.ext.commands import Context, command
from discord.ext.commands.cog import Cog
from src.music.client import MusicClient
from src.bebot import Bebot
from typing import cast
from discord import Guild, Member, VoiceState, VoiceChannel


class MusicCog(Cog, name = "Music"):
    def __init__(self, bot: Bebot):
        self.bot = bot

    @command(aliases=["p"], name="play")
    async def play(self, ctx: Context, *, search: str):
        songs = music_service.search_songs(search)
        author = cast(Member, ctx.author)
        voice_state = cast(VoiceState, author.voice)
        music_client = self.get_music_client(ctx)
        await music_client.connect(cast(VoiceChannel, voice_state.channel))
        await music_client.queue_songs(songs)

    @play.before_invoke
    async def check_voice_channel(self, ctx: Context):
        author = cast(Member, ctx.author)
        if not author.voice or not author.voice.channel:
            raise exceptions.UserNotConnectedToVoiceChannel()

        if ctx.voice_client and ctx.voice_client.channel != author.voice.channel:
            raise exceptions.BotConnectedToAnotherChannel()

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
