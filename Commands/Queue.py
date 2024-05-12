import discord
import EmbedUtils
import Constants
from .Util.CommandUtils import definecmd, fetch_check, playing_check, channel_check
from PYMusicBot import PYMusicBot
from Player.PlayerInstance import PlayerInstance
from Player.PageView import PageView

@definecmd("queue", 
           "Lists the player's queue")
async def cmd_queue(e : discord.Interaction):
    client : PYMusicBot = e.client
    player : PlayerInstance | None = client.get_player(e.guild)

    # if not await playing_check(e, player) or not await channel_check(e, player) or not await fetch_check(e, player):
    #     return

    view = PageView([ "First page", "Second page", "Third page", "Fourth page" ])
    await e.response.send_message(content=view.pages[0], view=view)