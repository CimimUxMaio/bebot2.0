import discord
import discord.ui as ui
from discord import Embed, Interaction, Message, TextChannel


def MainEmbed(music_state) -> Embed:
    embed = Embed(color=discord.Color.random())
    current_song = music_state["current"]
    current_msg = current_song if current_song else "Nada... que aburrido."
    embed.add_field(name = "Escuchando:", value = current_msg, inline=False)
    embed.set_image(url = "attachment://music_playing.gif")
    return embed


class MainView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="Prev")
    async def previous(self, interaction: Interaction, _: ui.Button):
        print("Prev")
        await interaction.response.defer()

    @ui.button(label="Play/Stop")
    async def play_stop(self, interaction: Interaction, _: ui.Button):
        print("Play/Stop")
        await interaction.response.defer()

    @ui.button(label="Next")
    async def next(self, interaction: Interaction, _: ui.Button):
        print("Next")
        await interaction.response.defer()

    @ui.button(label="Queue")
    async def queue(self, interaction: Interaction, _: ui.Button):
        print("Queue")
        await interaction.response.defer()


async def send_main_message(channel: TextChannel) -> Message:
    profile_pic = discord.File("./assets/music_playing.gif", filename="music_playing.gif")
    music_state = {"current": "Cancion 1", "status": "paused"}
    main_message = await channel.send(embed=MainEmbed(music_state), view=MainView(), files=[profile_pic])
    # await main_message.add_reaction("\N{DOUBLE VERTICAL BAR}")
    return main_message

    

