import discord
import EmbedUtils
from .Util.CommandUtils import definecmd, guild_check, fetch_check, playing_check
from PYMusicBot import PYMusicBot
from Player.PlayerInstance import PlayerInstance

@definecmd("whoinvoked", 
           "See who invoked the player in the voice channel")
async def cmd_whoinvoked(e : discord.Interaction):
    if not await guild_check(e): return
    client : PYMusicBot = e.client
    player : PlayerInstance | None = client.get_player(e.guild)

    if not await playing_check(e, player) or not await fetch_check(e, player):
        return

    await e.response.send_message(embed=EmbedUtils.state(None, None, player.invoker))