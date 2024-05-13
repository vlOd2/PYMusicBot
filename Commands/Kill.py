import discord
import EmbedUtils
from .Util.CommandUtils import definecmd, admin_check, guild_user_check, playing_check
from PYMusicBot import PYMusicBot
from Player.PlayerInstance import PlayerInstance

@definecmd("kill", 
           "Kills all player instances (admin only)")
async def cmd_kill(e : discord.Interaction):
    if not await guild_user_check(e): return
    client : PYMusicBot = e.client

    if not await admin_check(e):
        return

    await client.destroy_players()

    await e.response.send_message(embed=EmbedUtils.state(
        "Killed all player instances", None, e.user))