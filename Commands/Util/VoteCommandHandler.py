# Handler for vote commands
import discord
import logging
import EmbedUtils
from .CommandUtils import admin_check, fetch_check, playing_check, channel_check
from PYMusicBot import PYMusicBot
from Player.PlayerInstance import PlayerInstance
from Player.VotingView import VotingView
from Utils import required_votes
from typing import Callable

async def handle_vote(e : discord.Interaction,
                      check_instant : Callable[[PlayerInstance], bool],
                      on_success : Callable[[PYMusicBot, PlayerInstance], None], 
                      action_id : str, 
                      instant_body : str,
                      force : bool = False): 
    client : PYMusicBot = e.client
    player : PlayerInstance | None = client.get_player(e.guild)

    if not await playing_check(e, player) or not await channel_check(e, player) or not await fetch_check(e, player):
        return

    logger = logging.getLogger("VoteCommandHandler")

    async def on_success_wrapper():
        logger.info(f"{action_id} vote was successful")
        await on_success(client, player)

    if check_instant(player) or force:
        if force and not await admin_check(e):
            return
        logger.info(f"{e.user.name} ({e.user.id}) has done an instant vote: {action_id}")
        await e.response.send_message(embed=EmbedUtils.success(
            f"Instant vote{" (forced)" if force else ""}", 
            instant_body if not force else None, 
            e.user))
        await on_success_wrapper()
        return

    logger.info(f"{e.user.name} ({e.user.id}) has started a vote: {action_id}")
    view = VotingView(action_id, required_votes(player.channel), e.user, on_success_wrapper)
    await e.response.send_message(content="Loading vote, please wait...", view=view)
    view.msg = await e.original_response()

    await view._update()