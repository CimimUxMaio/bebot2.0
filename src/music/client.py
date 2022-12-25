import asyncio
import src.exceptions as exceptions
import src.messages.mainmsg as mainmsg

from discord import VoiceClient
from asyncio import Queue, Event
from src.music.service import Song
from dataclasses import dataclass

@dataclass
class MusicState:
    current_song: Song | None 


class MusicClient:
    def __init__(self, bot, guild_id: int):
        self.bot = bot
        self.guild_id = guild_id

        self.voice_client: VoiceClient | None = None
        self._queue: Queue[Song] = Queue()
        self.current_song: Song | None = None
        self.next_song_event: Event = Event()

        self.init_audio_player()

    def init_audio_player(self):
        self.audio_player = self.bot.loop.create_task(self.play_loop())

    def is_connected(self):
        return self.voice_client is not None and self.voice_client.is_connected()

    def queue(self) -> list[Song]:
        return list(self._queue.__dict__["_queue"])

    async def play_loop(self):
        try:
            while True:
                self.next_song_event.clear()

                try:
                    self.current_song = await self.get_next_song(timeout=60)
                    # self._queue.task_done()
                except asyncio.TimeoutError:
                    await self.run_finish_task()
                    return

                # Update main message with current song
                await self.send_update()

                # Play song
                vc = self.require_voice_client()
                vc.play(self.current_song.audio, after = self.play_next_song)

                # Wait until the song has finished.
                await self.next_song_event.wait()

                # Update main message with no song
                if self._queue.empty():
                    await self.send_update()
        except Exception as e:
            # Something went wrong during the play loop.
            await self.run_finish_task()
            raise e

    async def get_next_song(self, *, timeout = None) -> Song:
        return await asyncio.wait_for(self._queue.get(), timeout = timeout)

    async def run_finish_task(self):
        self.bot.loop.create_task(self.finish())

    async def finish(self):
        # Clean-up
        self._queue = Queue()
        self.current_song = None

        if self.voice_client:
            await self.voice_client.disconnect()
            self.voice_client = None

        # Update main message
        await self.send_update()
        
    def play_next_song(self, error: Exception | None = None):
        # Ignore error, if something went wrong during the previous song continue 
        # with the next one.
        if error:
            print(str(error))

        self.current_song = None
        self.next_song_event.set()

    async def connect(self, voice_channel):
        if self.audio_player.done():
            self.init_audio_player()

        if self.voice_client:
            await self.voice_client.move_to(voice_channel)
            return

        self.voice_client = await voice_channel.connect()

    async def disconnect(self):
        self.audio_player.cancel()
        await self.finish()

    async def queue_songs(self, songs: list[Song]):
        for song in songs:
            await self._queue.put(song)

    def require_voice_client(self) -> VoiceClient:
        if not self.voice_client:
            raise exceptions.VoiceClientNotSet()

        return self.voice_client

    def toggle_pause_resume(self):
        vc = self.require_voice_client()
        if vc.is_paused():
            vc.resume()
        elif vc.is_playing():
            vc.pause()

    def skip_current_song(self):
        vc = self.require_voice_client()
        self.current_song = None
        vc.stop()

    async def send_update(self):
        main_message = await self.bot.fetch_or_set_main_message(self.guild_id)
        await mainmsg.update(main_message, self.state())

    def state(self) -> MusicState:
        return MusicState(current_song=self.current_song)
