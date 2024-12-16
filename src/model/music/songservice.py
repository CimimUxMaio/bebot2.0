import asyncio
import src.exceptions as exceptions

from typing import Any, Callable, TypeVar
from yt_dlp import YoutubeDL
from validators.url import url as is_url
from concurrent.futures import ThreadPoolExecutor
from src.model.music.song import Song, SongInfo, Duration
from discord.player import FFmpegPCMAudio


Entry = dict[str, Any]
Options = dict[str, Any]


FFMPEG_OPTIONS: dict[str, Any] = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}

EXECUTOR = ThreadPoolExecutor(max_workers=3)


def seconds_to_duration(seconds: int) -> Duration:
    hours, remainder = divmod(seconds, 3600)
    minutes, remainder = divmod(remainder, 60)
    secs = remainder % 60
    return hours, minutes, secs


def entry_to_song_info(entry: Entry) -> SongInfo:
    return SongInfo(
        title=entry["title"],
        duration=seconds_to_duration(entry["duration"]),
        url=entry["url"],
        author=entry["channel"],
    )


def entry_to_song(entry: Entry) -> Song:
    info = entry_to_song_info(entry)
    return Song(
        info=info,
        audio=FFmpegPCMAudio(info.url, **FFMPEG_OPTIONS),
        thumbnail_url=entry["thumbnail"],
    )


T = TypeVar("T")


def ytdl_search_sync(search: str, opts: Options, func: Callable[[Entry], T]) -> list[T]:
    with YoutubeDL(opts) as ydl:
        try:
            info = ydl.extract_info(search, download=False)
        except Exception as e:
            print(e)
            return []

    if info is None:
        return []

    entries = [info]
    if "_type" in info and info["_type"] == "playlist":
        entries = info["entries"]

    return list(map(func, entries))  # type: ignore


async def ytdl_search(
    search: str, opts: Options, func: Callable[[Entry], T]
) -> list[T]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(EXECUTOR, ytdl_search_sync, search, opts, func)


async def ytdl_search_info(search: str, n: int = 5) -> list[SongInfo]:
    opts = {"extract_flat": True}
    return await ytdl_search(f"ytsearch{n}:{search}", opts, entry_to_song_info)


async def ytdl_get_song(search: str) -> Song:
    opts = {"format": "bestaudio"}

    if not is_url(search):
        search = f"ytsearch1:{search}"

    songs = await ytdl_search(search, opts, entry_to_song)

    if len(songs) == 0:
        raise exceptions.SongNotFound(search)

    return songs[0]
