import discord
import discord.ui as ui
import src.strings as strings

from discord import Embed, Interaction, Message, TextChannel


def MainEmbed(music_state) -> Embed:
    embed = Embed(color=discord.Color.random())
    current_song = music_state["current"]
    current_msg = current_song if current_song else strings.NOTHING_PLAYING
    embed.add_field(name = strings.NOW_PLAYING, value = current_msg, inline=False)
    embed.set_image(url = "attachment://music_playing.gif")
    return embed


class MainView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label=strings.PREV_BUTTON_LABEL)
    async def previous(self, interaction: Interaction, _: ui.Button):
        print("Prev")
        await interaction.response.defer()

    @ui.button(label=strings.PLAY_STOP_BUTTON_LABEL)
    async def play_stop(self, interaction: Interaction, _: ui.Button):
        print("Play/Stop")
        await interaction.response.defer()

    @ui.button(label=strings.NEXT_BUTTON_LABEL)
    async def next(self, interaction: Interaction, _: ui.Button):
        print("Next")
        await interaction.response.defer()

    @ui.button(label=strings.QUEUE_BUTTON_LABEL)
    async def queue(self, interaction: Interaction, _: ui.Button):
        print("Queue")
        await interaction.response.defer()


async def send(channel: TextChannel) -> Message:
    profile_pic = discord.File("./assets/music_playing.gif", filename="music_playing.gif")
    music_state = {"current": "Cancion 1", "status": "paused"}
    main_message = await channel.send(embed=MainEmbed(music_state), view=MainView(), files=[profile_pic])
    # await main_message.add_reaction("\N{DOUBLE VERTICAL BAR}")
    return main_message

    

