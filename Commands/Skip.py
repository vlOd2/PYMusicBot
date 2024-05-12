import discord
import EmbedUtils
from .CommandUtils import definecmd, fetch_check, playing_check, channel_check
from PYMusicBot import PYMusicBot
from Player.PlayerInstance import PlayerInstance
from Player.VotingView import VotingView
from Utils import required_votes

@definecmd("skip", 
           "Skips the currently playing song (requires voting)")
async def cmd_skip(e : discord.Interaction):
    client : PYMusicBot = e.client
    player : PlayerInstance | None = client.get_player(e.guild)

    if not await playing_check(e, player) or not await channel_check(e, player) or not await fetch_check(e, player):
        return

    if e.user.id == player.current_source[0].invoker.id:
        await e.response.send_message(embed=EmbedUtils.success(
            "Instantly skipped the song",
            "Since you requested this song, you have instantly skipped it!",
            e.user
        ))
        player.skip()
        return

    async def on_success(): 
        player.skip()

    view = VotingView("skip", required_votes(player.channel), e.user, on_success)
    await e.response.send_message(content="Loading vote, please wait...", view=view)
    view.msg = await e.original_response()

    await view.update()