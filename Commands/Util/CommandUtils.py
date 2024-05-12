# Utilities used by commands or similar
import discord
import EmbedUtils
from discord.app_commands import commands
from Player.PlayerInstance import PlayerInstance

DefinedCommands : list[commands.Command] = []

# Custom decorator that makes it so easy to add all the commands
def definecmd(name : str, description : str):
    def decorator(func):
        cmd = commands.Command(name=name, description=description, callback=func)
        DefinedCommands.append(cmd)
    return decorator

async def fetch_check(e : discord.Interaction, player : PlayerInstance) -> bool:
    if player.current_source == None:
        await e.response.send_message(embed=EmbedUtils.error(
            "Too soon",
            "Wait for the first song to get fetched before running this",
            e.user
        ), ephemeral=True)
        return False
    return True

async def playing_check(e : discord.Interaction, player : PlayerInstance) -> bool:
    if player == None:
        await e.response.send_message(embed=EmbedUtils.error(
            "Not connected",
            "Not currently connected in a voice channel",
            e.user
        ), ephemeral=True)
        return False
    return True

async def channel_check(e : discord.Interaction, player : PlayerInstance) -> bool:
    if player != None and (e.user.voice == None or e.user.voice.channel.id != player.channel.id):
        await e.response.send_message(embed=EmbedUtils.error(
            "Mismatched channel",
            "You are not currently in my voice channel",
            e.user
        ), ephemeral=True)
        return False
    
    return True