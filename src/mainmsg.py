import discord
import discord.ui as ui
import src.strings as strings

from discord import Embed, Interaction, Message, TextChannel
from src.guildstaterepo import GuildState
from src.music.client import MusicClient, MusicState


def MainEmbed(music_state: MusicState | None = None) -> Embed:
    embed = Embed(color=discord.Color.random())

    if not music_state or not music_state.current_song:
        current_msg = strings.NOTHING_PLAYING
    else:
        current_msg = music_state.current_song.title

    embed.add_field(name = strings.NOW_PLAYING, value = current_msg, inline=False)
    embed.set_image(url = "attachment://status.gif")
    return embed


class MainView(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    # @ui.button(label=strings.PREV_BUTTON_LABEL)
    # async def previous(self, interaction: Interaction, _: ui.Button):
    #     print("Prev")
    #     await interaction.response.defer()

    @ui.button(label=strings.PLAY_STOP_BUTTON_LABEL)
    async def stop_resume(self, interaction: Interaction, _: ui.Button):
        if interaction.guild_id:
            music_client = self.get_music_client(interaction.guild_id)
            music_client.toggle_pause_resume()
        await interaction.response.defer()

    @ui.button(label=strings.NEXT_BUTTON_LABEL)
    async def next(self, interaction: Interaction, _: ui.Button):
        if interaction.guild_id:
            music_client = self.get_music_client(interaction.guild_id)
            music_client.skip_current_song()
        await interaction.response.defer()

    @ui.button(label=strings.QUEUE_BUTTON_LABEL)
    async def queue(self, interaction: Interaction, _: ui.Button):
        print("Queue")
        await interaction.response.defer()

    def get_music_client(self, guild_id: int) -> MusicClient:
        state: GuildState = self.bot.state_repo.get(guild_id)
        return state.music_client

async def send(bot, channel: TextChannel) -> Message:
    profile_pic = discord.File("./assets/music_playing.gif", filename="status.gif")
    return await channel.send(embed=MainEmbed(), view=MainView(bot), files=[profile_pic])

async def update(message: Message, state: MusicState) -> Message:
    profile_pic = discord.File("./assets/music_playing.gif", filename="status.gif")
    return await message.edit(embed=MainEmbed(state), attachments=[profile_pic])

