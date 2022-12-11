from discord import Embed, Interaction, Message, TextChannel
from discord.ui.button import Button
from discord.ui.view import View


class ExampleButton(Button):
    counter = 0

    def __init__(self):
        super().__init__(label="Click Me!")

    async def callback(self, interaction: Interaction):
        print("Button clicked!", self.counter)
        self.counter += 1
        await interaction.response.defer()

class MainView(View):
    def __init__(self):
        self.add_item(ExampleButton())
        
class MainEmbed(Embed):
    def __init__(self):
        self.add_field(name = "Field 1", value = "A field")

class MainMsgContent:
    def view(self) -> View:
        view = View()
        view.add_item(ExampleButton())
        return view

    def embed(self) -> Embed:
        embed = Embed()
        embed.add_field(name = "Field 1", value = "A field")
        return embed

    async def send(self, channel: TextChannel) -> Message:
        return await channel.send(embed=self.embed(), view=self.view())
