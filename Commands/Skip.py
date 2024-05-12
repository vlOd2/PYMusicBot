import discord
from .Util.CommandUtils import definecmd
from .Util.VoteCommandHandler import handle_vote
from Player.PlayerInstance import PlayerInstance

@definecmd("skip", 
           "Skips the currently playing song")
async def cmd_skip(e : discord.Interaction):
    async def on_success(client, player : PlayerInstance):
        player.skip()
    await handle_vote(e, on_success, "skip", 
                        "You have instantly skipped the current song since you queued it")