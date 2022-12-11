import discord.ui as ui
from discord import Embed, Interaction, Message, TextChannel


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


class MainMenu:
    def embed(self) -> Embed:
        embed = Embed()
        embed.add_field(name = "Field 1", value = "A field")
        return embed

    async def send(self, channel: TextChannel) -> Message:
        return await channel.send(embed=self.embed(), view=MainView())

