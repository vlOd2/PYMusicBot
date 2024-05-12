# Handler for vote commands
import discord
import EmbedUtils
from .CommandUtils import fetch_check, playing_check, channel_check
from PYMusicBot import PYMusicBot
from Player.PlayerInstance import PlayerInstance
from Player.VotingView import VotingView
from Utils import required_votes
from typing import Callable

async def handle_vote(e : discord.Interaction, 
                        on_success : Callable[[PYMusicBot, PlayerInstance], None], 
                        action_id : str, 
                        instant_body : str):
    client : PYMusicBot = e.client
    player : PlayerInstance | None = client.get_player(e.guild)

    if not await playing_check(e, player) or not await channel_check(e, player) or not await fetch_check(e, player):
        return

    async def on_success_wrapper():
        await on_success(client, player)

    if e.user.id == player.current_source[0].invoker.id:
        await e.response.send_message(embed=EmbedUtils.success("Instant vote", instant_body, e.user))
        await on_success_wrapper()
        return

    view = VotingView(action_id, required_votes(player.channel), e.user, on_success_wrapper)
    await e.response.send_message(content="Loading vote, please wait...", view=view)
    view.msg = await e.original_response()

    await view.update()