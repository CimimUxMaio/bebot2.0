import asyncio
import src.exceptions as exceptions

from validators.url import url as is_url
from youtube_dl import YoutubeDL
from discord.player import FFmpegPCMAudio
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor


YDL_OPTIONS = {"format": "bestaudio"}

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"
}

EXECUTOR = ThreadPoolExecutor(max_workers=5)


@dataclass
class Song:
    title: str
    duration_desc: str
    audio: FFmpegPCMAudio


def duration_desc(song_info) -> str:
    duration = song_info["duration"]
    hours, remainder = divmod(duration, 3600)
    minutes, remainder = divmod(remainder, 60)
    seconds = remainder % 60

    def pad(n):
        return str(n).ljust(2, "0")

    return f"{pad(hours)}:{pad(minutes)}:{pad(seconds)}"


def download_song_sync(search: str) -> Song:
    with YoutubeDL(YDL_OPTIONS) as ydl:
        url = "ytsearch:%s" % search
        if is_url(search):  # type: ignore
            url = search

    try:
        info = ydl.extract_info(url, download=False)
    except:  # noqa: E722
        raise exceptions.SongNotFound(search)

    if not isinstance(info, dict):
        raise exceptions.UnexpectedSongResponse(search)

    try:
        song_info = info["entries"][0]
    except IndexError:
        raise exceptions.SongNotFound(search)

    return Song(
        title=song_info["title"],
        duration_desc=duration_desc(song_info),
        audio=FFmpegPCMAudio(song_info["url"], **FFMPEG_OPTIONS)
    )


async def download_song(search: str) -> Song:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(EXECUTOR, download_song_sync, search)
