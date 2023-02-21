import src.exceptions as exceptions
from validators.url import url as is_url

from youtube_dl import YoutubeDL
from discord.player import FFmpegPCMAudio
from dataclasses import dataclass


YDL_OPTIONS = {"format": "bestaudio"}

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"
}


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


def search_songs(search: str) -> list[Song]:
    with YoutubeDL(YDL_OPTIONS) as ydl:
        url = "ytsearch:%s" % search
        if is_url(search):  # type: ignore
            url = search

        info = ydl.extract_info(url, download=False)

    if not isinstance(info, dict):
        raise exceptions.UnexpectedSongResponse(search)

    try:
        songs_info = info["entries"]
    except IndexError:
        raise exceptions.SongNotFound(search)

    return [Song(
        title=info["title"],
        duration_desc=duration_desc(info),
        audio=FFmpegPCMAudio(info["url"], **FFMPEG_OPTIONS)
    ) for info in songs_info]
