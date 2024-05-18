import discord
import EmbedUtils
import logging
from .Util.CommandUtils import definecmd, guild_user_check, fetch_check, playing_check, channel_check
from PYMusicBot import PYMusicBot
from Player.PlayerInstance import PlayerInstance

@definecmd("repeat", 
           "Sets/gets the repeat status")
@discord.app_commands.describe(new_state="The new repeat state")
async def cmd_repeat(e : discord.Interaction, new_state : bool | None = None):
    if not await guild_user_check(e): return
    client : PYMusicBot = e.client
    player : PlayerInstance | None = client.get_player(e.guild)

    if not await playing_check(e, player) or not await channel_check(e, player) or not await fetch_check(e, player):
        return

    if new_state == None:
        await e.response.send_message(embed=EmbedUtils.state(
            f"Current repeat state: {player.repeat}", None, e.user), ephemeral=True)
        return
    
    player.repeat = new_state
    player.logger.info(f"{e.user.name}/{e.user.id}: Repeat state set to {player.repeat}")

    await e.response.send_message(embed=EmbedUtils.state(
        "Repeat state updated",
        f"The repeat state was updated to: {player.repeat}", 
        e.user
    ))