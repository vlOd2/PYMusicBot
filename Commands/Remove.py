import discord
import EmbedUtils
from .Util.CommandUtils import definecmd, guild_user_check, fetch_check, playing_check, channel_check
from PYMusicBot import PYMusicBot
from Player.PlayerInstance import PlayerInstance

@definecmd("remove", 
           "Removes an item from the queue")
async def cmd_remove(e : discord.Interaction, index : int):
    if not await guild_user_check(e): return
    client : PYMusicBot = e.client
    player : PlayerInstance | None = client.get_player(e.guild)

    if not await playing_check(e, player) or not await channel_check(e, player) or not await fetch_check(e, player):
        return

    await e.response.send_message(embed=EmbedUtils.state(
        "I'm alive!",
        "The bot is working perfectly fine!",
        e.user
    ))