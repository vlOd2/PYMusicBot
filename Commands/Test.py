import discord
import EmbedUtils
from .CommandDefinitions import definecmd

@definecmd("test", 
           "A test command that allows you to verify the bot's status")
async def cmd_test(e : discord.Interaction):
    await e.response.send_message(embed=EmbedUtils.state(
        "I'm alive!",
        "The bot is working perfectly fine!",
        e.user
    ))