import discord
import EmbedUtils
from .Util.CommandUtils import definecmd, guild_user_check, fetch_check, playing_check, channel_check
from PYMusicBot import PYMusicBot
from Player.PlayerInstance import PlayerInstance

#@definecmd("search", 
#           "Searches for at most 25 results for the specified query")
async def cmd_search(e : discord.Interaction):
    if not await guild_user_check(e): return
    client : PYMusicBot = e.client
    player : PlayerInstance | None = client.get_player(e.guild)

    if not await playing_check(e, player) or not await channel_check(e, player) or not await fetch_check(e, player):
        return
    
    await e.response.send_message("TODO: Stub command")