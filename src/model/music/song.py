from discord.player import FFmpegPCMAudio
from dataclasses import dataclass


Duration = tuple[int, int, int]


@dataclass
class SongInfo:
    title: str
    duration: Duration | None
    author: str
    url: str


@dataclass
class Song:
    info: SongInfo
    thumbnail_url: str
    audio: FFmpegPCMAudio
