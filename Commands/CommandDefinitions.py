import discord
import EmbedUtils
from discord.app_commands import commands
from Player.PlayerInstance import PlayerInstance

DefinedCommands : list[commands.Command] = []

def definecmd(name, description):
    def decorator(func):
        cmd = commands.Command(name=name, description=description, callback=func)
        DefinedCommands.append(cmd)
    return decorator

async def invoker_channel_checks(e : discord.Interaction, player : PlayerInstance, client) -> bool:
    if player == None and e.user.voice == None:
        await e.response.send_message(embed=EmbedUtils.error(
            "Failed to join",
            "You are not currently in a voice channel",
            client,
            e.user
        ), ephemeral=True)
        return False

    if player != None and (e.user.voice == None or e.user.voice.channel.id != player.channel.id):
        await e.response.send_message(embed=EmbedUtils.error(
            "Mismatched channel",
            "You are not currently in my voice channel",
            client,
            e.user
        ), ephemeral=True)
        return False
    
    return True