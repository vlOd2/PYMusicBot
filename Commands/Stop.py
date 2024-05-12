import discord
from .Util.CommandUtils import definecmd
from .Util.VoteCommandHandler import handle_vote
from Player.PlayerInstance import PlayerInstance

@definecmd("stop", 
           "Clears the queue and disconnects")
async def cmd_stop(e : discord.Interaction):
    async def on_success(client, player : PlayerInstance):
        await player.stop()
    await handle_vote(e, on_success, "stop", 
                        "You have instantly stopped the player since you invoked it!")