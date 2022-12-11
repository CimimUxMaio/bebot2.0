import discord.ui as ui
from discord import Embed, Interaction, Message, TextChannel


class MainView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="Button 1")
    async def button1(self, interaction: Interaction, _: ui.Button):
        print("Clicked button 1")
        await interaction.response.defer()

    @ui.button(label="Button 2")
    async def button2(self, interaction: Interaction, _: ui.Button):
        print("Clicked button 2")
        await interaction.response.defer()


class MainMenu:
    def embed(self) -> Embed:
        embed = Embed()
        embed.add_field(name = "Field 1", value = "A field")
        return embed

    async def send(self, channel: TextChannel) -> Message:
        return await channel.send(embed=self.embed(), view=MainView())
