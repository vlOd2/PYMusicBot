import discord
from .Util.CommandUtils import definecmd, guild_user_check
from .Util.VoteCommandHandler import handle_vote
from Player.PlayerInstance import PlayerInstance

@definecmd("skip", 
           "Skips the currently playing song")
async def cmd_skip(e : discord.Interaction, force : bool = False):
    if not await guild_user_check(e): return
    
    async def on_success(client, player : PlayerInstance):
        player.skip()

    await handle_vote(e, 
                      lambda player: e.user.id == player.current_source[0].invoker.id,
                      on_success, 
                      "skip", 
                      "You have instantly skipped the current song since you queued it",
                      force)