import discord
from discord.ext import commands 

client=commands.Bot(command_prefix=".")

class Buttons(discord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)
    @discord.ui.button(label="Button",style=discord.ButtonStyle.gray)
    async def gray_button(self,button:discord.ui.Button,interaction:discord.Interaction):
        await interaction.response.edit_message(content=f"This is an edited button response!")

@client.command()
async def button(ctx):
    await ctx.send("This message has buttons!",view=Buttons())

client.run("OTgyNzY0NDkyMDAzODkzMzU5.Gw2mUv.UL7TCa5qLEJYUgcprFFseiO-liiKN0Wg118P3k")