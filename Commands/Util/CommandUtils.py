# Utilities used by commands or similar
import inspect
import discord
import EmbedUtils
from Config import ConfigInstance as Config
from discord.app_commands import commands
from Player.PlayerInstance import PlayerInstance

DefinedCommands : list[commands.Command] = []

# Custom decorator that makes it so easy to add all the commands
def definecmd(name : str, description : str):
    def decorator(func):
        if not inspect.iscoroutinefunction(func):
            raise TypeError("Not a coroutine!")
        cmd = commands.Command(name=name, 
                               description=description, 
                               callback=func)
        DefinedCommands.append(cmd)
        return cmd
    return decorator

async def admin_check(e : discord.Interaction) -> bool:
    if e.user.id in Config.AdminUsers:
        return True
    else:
        for role in e.user.roles:
            if role.id in Config.AdminRoles:
                return True

    await e.response.send_message(embed=EmbedUtils.error(
        "Insufficient permissions",
        ("Only administrators are allowed to run this command\n" + 
        f"NOTE: Admins in this context doesn't mean server admins"),
        e.user
    ), ephemeral=True)
    return False

async def guild_user_check(e : discord.Interaction) -> bool:
    if e.guild == None:
        await e.response.send_message(embed=EmbedUtils.error(
            "Not available",
            "Commands are only available in a guild",
            e.user
        ), ephemeral=True)
        return False

    if e.user.id in Config.BannedUsers:
        # Let the command time out
        return False

    return True

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
            "Player not connected",
            "The player is not currently connected in a voice channel",
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