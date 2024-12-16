import emoji
import src.exceptions as exceptions
import src.model.music.songservice as songservice

from functools import wraps
from typing import cast
from discord import Embed, Member, Guild, Message, NotFound, VoiceState, Color
from discord.channel import VocalGuildChannel
from discord.ext.commands import Context, command
from validators.url import url as is_url

from src.bebot import Bebot
from src.cogs.base import BaseCog
from src.model.music.musicplayer import MusicPlayer
from src.model.music.song import Song, SongInfo
from src.strings import commands as commandstr

NUMBER_EMOJIS = [
    emoji.emojize(alias, language="alias")
    for alias in [
        ":one:",
        ":two:",
        ":three:",
        ":four:",
        ":five:",
        ":six:",
        ":seven:",
        ":eight:",
        ":nine:",
    ]
]


def check_voice_requirements(func):
    @wraps(func)
    async def decorator(self, ctx: Context, *args, **kwargs):
        author = cast(Member, ctx.author)

        # Check if the author is not connected to a voice channel
        if author.voice is None or author.voice.channel is None:
            raise exceptions.UserNotConnectedToVoiceChannel()

        music_player = self.get_music_player(ctx)
        channel = music_player.get_channel()

        # Check if the bot is connected to a different voice channel
        if channel is not None and channel != author.voice.channel:
            raise exceptions.BotConnectedToAnotherChannel()

        return await func(self, ctx, *args, **kwargs)

    return decorator


def with_status_message(func):
    @wraps(func)
    async def decorator(self, ctx: Context, *args, **kwargs):
        await func(self, ctx, *args, **kwargs)
        guild_id = cast(Guild, ctx.guild).id
        message = await ctx.send(embed=self.status_message(guild_id))
        self.update_last_status(ctx, message)

    return decorator


class MusicCog(BaseCog, name="Music"):
    def __init__(self, bot):
        super().__init__(bot)
        self.music_players: dict[int, MusicPlayer] = {}
        self.last_status: dict[int, Message] = {}

    # Commands #

    @command(
        name="play",
        aliases=["p"],
        help=commandstr.PLAY_HELP,
    )
    @check_voice_requirements
    @with_status_message
    async def play(self, ctx: Context, *, search: str):
        music_player = self.get_music_player(cast(Guild, ctx.guild).id)

        search = search.strip()

        url = search
        if not is_url(search):
            # Send song selection message
            url = await self.song_selection(ctx, search)

        # If the user does not select a song, delete the results message and return
        if url is None or len(url) == 0:
            await ctx.reply(commandstr.PLAY_SELECTION_TIMEOUT)
            return

        # Search song by url and add it to the queue
        async with ctx.typing():
            song: Song = await songservice.ytdl_get_song(url)
            await music_player.add(song)

            # If the player is not connected, connect to the author's voice channel
            if not music_player.is_connected():
                channel: VocalGuildChannel = cast(VoiceState, ctx.author.voice).channel  # type: ignore
                await music_player.connect(channel)

            await ctx.reply(commandstr.PLAY_ADDED_TO_QUEUE.format(song.info.title))

    @command(name="pause", help=commandstr.PAUSE_HELP)
    @check_voice_requirements
    @with_status_message
    async def pause(self, ctx: Context):
        await self.get_music_player(cast(Guild, ctx.guild).id).toggle_pause_resume()

    @command(
        name="stop",
        help=commandstr.STOP_HELP,
    )
    @check_voice_requirements
    @with_status_message
    async def stop(self, ctx: Context):
        await self.get_music_player(cast(Guild, ctx.guild).id).stop()

    @command(
        name="skip",
        aliases=["next", "s"],
        help=commandstr.SKIP_HELP,
    )
    @check_voice_requirements
    @with_status_message
    async def skip(self, ctx: Context):
        self.get_music_player(cast(Guild, ctx.guild).id).next()

    @command(
        name="queue",
        aliases=["q"],
        help=commandstr.QUEUE_HELP,
    )
    async def queue(self, ctx: Context):
        guild_id = cast(Guild, ctx.guild).id
        message = await ctx.reply(embed=self.status_message(guild_id))
        self.update_last_status(ctx, message)

    # Utility methods #

    def get_music_player(self, guild_id: int) -> MusicPlayer:
        player = self.music_players.get(guild_id, None)

        # Return existing music player
        if player is not None:
            return player

        # Initialize new music player if none found
        player = MusicPlayer()

        def on_status_update():
            return self.on_player_status_update(guild_id)

        self.bot.loop.create_task(
            player.run(on_status_update)
        )  # Start the music player
        self.music_players[guild_id] = player

        return player

    async def get_last_status(self, guild_id: int) -> Message | None:
        message = self.last_status.get(guild_id, None)

        if message is not None:
            try:
                # Check if the message still exists
                message = await message.fetch()
            except NotFound:
                # If not, remove it from the last status dictionary
                del self.last_status[guild_id]
                message = None

        return message

    def update_last_status(self, ctx: Context, message: Message):
        guild_id = cast(Guild, ctx.guild).id
        self.last_status[guild_id] = message

    def search_results_embed(self, results: list[SongInfo]):
        embed = Embed(title=commandstr.SONG_SELECTION_TITLE, color=Color.blue())

        for i, info in enumerate(results):
            author = f"{commandstr.SONG_AUTHOR_LABEL} {info.author}"
            duration = (
                f"{commandstr.SONG_DURATION_LABEL} %02i:%02i:%02i" % info.duration
            )

            embed.add_field(
                name=f"{NUMBER_EMOJIS[i]} {info.title}",
                value=f"{author} - {duration}",
                inline=False,
            )

        embed.set_footer(text=commandstr.SONG_SELECTION_FOOTER)
        return embed

    async def song_selection(self, ctx: Context, search: str) -> str | None:
        # Search youtube results
        async with ctx.typing():
            results = await songservice.ytdl_search_info(search)
            results_msg = await ctx.reply(embed=self.search_results_embed(results))

        # Add show selection embed menu
        options = NUMBER_EMOJIS[: len(results)]
        for option in options:
            await results_msg.add_reaction(option)

        def check_reaction(reaction, user):
            return user == ctx.author and str(reaction) in options

        try:
            reaction, _ = await self.bot.wait_for(
                "reaction_add", check=check_reaction, timeout=20
            )
        except TimeoutError:
            return None
        finally:
            # Remove the selection menu after the selection process
            await results_msg.delete()

        # Get the selected song index
        selection = options.index(str(reaction))
        return results[selection].url

    def status_message(self, guild_id: int) -> Embed:
        music_player = self.get_music_player(guild_id)
        song = music_player.get_current()

        embed = Embed(title=commandstr.STATUS_MESSAGE_TITLE, color=Color.blue())

        if song is None:
            embed.add_field(name="-", value=commandstr.STATUS_MESSAGE_EMPTY_QUEUE)
            return embed

        duracion = "%02i:%02i:%02i" % song.info.duration
        embed.add_field(
            name=song.info.title,
            value=f"{commandstr.SONG_DURATION_LABEL} {duracion} - {commandstr.SONG_AUTHOR_LABEL} {song.info.author}",
        )
        embed.set_thumbnail(url=song.thumbnail_url)

        queue_text = "-"
        queue = music_player.get_queue()
        if len(queue) > 0:
            queue_text = "\n".join(
                [
                    # Replace whitespace with special blank character to prevent
                    # discord from trimming initial whitespaces.
                    # Used 2 digit length for the number to keep the alignment.
                    f"{n:2d}. {song.info.title}".replace(" ", "\u1CBC")
                    for n, song in enumerate(queue, start=1)
                ]
            )

        embed.add_field(
            name=commandstr.STATUS_MESSAGE_QUEUE_TITLE, value=queue_text, inline=False
        )
        return embed

    async def on_player_status_update(self, guild_id: int):
        status_msg = await self.get_last_status(guild_id)

        if status_msg is not None:
            await status_msg.edit(embed=self.status_message(guild_id))


async def setup(bot: Bebot):
    await bot.add_cog(MusicCog(bot))
