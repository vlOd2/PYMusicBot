import discord
from .Util.CommandUtils import definecmd, guild_user_check
from .Util.VoteCommandHandler import handle_vote
from Player.PlayerInstance import PlayerInstance

@definecmd("stop", 
           "Clears the queue and disconnects")
async def cmd_stop(e : discord.Interaction):
    if not await guild_user_check(e): return
    
    async def on_success(client, player : PlayerInstance):
        await player.stop()

    await handle_vote(e, 
                      lambda player: e.user.id == player.invoker.id,
                      on_success, 
                      "stop", 
                      "You have instantly stopped the player since you invoked it!")