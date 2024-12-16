import asyncio

from asyncio import Queue, Event
from typing import Callable, Coroutine, cast
from discord import VoiceClient
from discord.channel import VocalGuildChannel
from src.model.music.song import Song


class MusicPlayer:
    def __init__(self):
        self.voice_client: VoiceClient | None = None
        self.song_queue: Queue[Song] = Queue()
        self.current_song: Song | None = None
        self.connection = Event()

    async def add(self, song: Song):
        await self.song_queue.put(song)

    def next(self):
        if self.voice_client is None:
            return

        self.voice_client.stop()

    def get_queue(self) -> list[Song]:
        return list(self.song_queue.__dict__["_queue"])

    def get_current(self) -> Song | None:
        return self.current_song

    async def toggle_pause_resume(self):
        if self.voice_client is None:
            return

        if self.voice_client.is_paused():
            self.voice_client.resume()
        elif self.voice_client.is_playing():
            self.voice_client.pause()

    async def stop(self):
        # Reset the music player
        self.song_queue = Queue()
        self.current_song = None
        await self.disconnect()

    async def run(self, on_update: Callable[[], Coroutine]):
        while True:
            try:
                # Wait for a voice client
                await self.connection.wait()

                try:
                    # Get next song in queue
                    self.current_song = await asyncio.wait_for(
                        self.song_queue.get(), timeout=60 * 3
                    )
                except asyncio.TimeoutError:
                    # Exit if there is no song in the queue after timeout
                    await self.stop()
                    await on_update()
                    continue

                # Event to signal when the song has ended
                song_ended = Event()

                def on_song_end(e):
                    if e is not None:
                        print(e)
                    song_ended.set()

                # Play the song
                # At this point, self.voice_client should not be None
                cast(VoiceClient, self.voice_client).play(
                    self.current_song.audio, after=on_song_end
                )

                await on_update()

                # Wait for the song to end
                await song_ended.wait()

            except Exception as e:
                await self.stop()
                print(e)

    async def connect(self, voice_channel: VocalGuildChannel):
        # If already connected, move to the new voice channel
        if self.is_connected():
            await cast(VoiceClient, self.voice_client).move_to(voice_channel)
            return

        # If not connected, connect and create a new voice client
        self.voice_client = await voice_channel.connect()
        self.connection.set()

    async def disconnect(self):
        if not self.is_connected():
            return

        # Disconnect from existing voice client
        await cast(VoiceClient, self.voice_client).disconnect()
        self.voice_client = None
        self.connection.clear()

    def is_connected(self) -> bool:
        return (
            self.voice_client is not None
            and self.voice_client.is_connected()
            and self.connection.is_set()
        )

    def get_channel(self) -> VocalGuildChannel | None:
        if self.voice_client is None:
            return None
        return cast(VoiceClient, self.voice_client).channel
