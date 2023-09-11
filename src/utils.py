import src.exceptions as exceptions

from typing import cast, TypeVar
from discord import Embed, Interaction, Member
from discord.ext.commands import Context
from discord.ui import View
from src.guildstaterepo import GuildState
from src.music.client import MusicClient


T = TypeVar("T")


def group(_list: list[T], group_size: int) -> list[list[T]]:
    return [_list[i: i + group_size] for i in range(0, len(_list), group_size)]


class SuperContext:
    def __init__(self, bot, ctx: Interaction | Context):
        self._ctx = ctx
        from src.bebot import Bebot  # Circular import
        self._bot: Bebot = bot

    @property
    def author(self) -> Member:
        if isinstance(self._ctx, Context):
            author = self._ctx.author
        else:  # Is Interaction
            author = self._ctx.user

        return cast(Member, author)

    async def send_message(
        self,
        content: str | None = None,
        *,
        embed: Embed | None = None,
        view: View | None = None,
        delete_after: float | None = None
    ):
        if isinstance(self._ctx, Context):
            return await self._ctx.send(
                content=content, embed=embed, view=view, delete_after=delete_after
            )
        else:  # Is Interaction
            if not embed:
                embed = Embed()
            if not view:
                view = View()

            return await self._ctx.response.send_message(
                content=content, embed=embed, view=view, delete_after=delete_after
            )

    async def check_voice_channel(self):
        if not self.author.voice or not self.author.voice.channel:
            raise exceptions.UserNotConnectedToVoiceChannel()

        guild = self._ctx.guild

        if not guild:
            raise exceptions.NotAGuildMessage()

        guild_id = guild.id
        music_client = self.get_music_client(guild_id)

        if music_client.voice_client and \
                music_client.voice_client.channel != self.author.voice.channel:
            raise exceptions.BotConnectedToAnotherChannel()

    def get_music_client(self, guild_id: int) -> MusicClient:
        state: GuildState = self._bot.state_repo.get(guild_id)
        return state.music_client
