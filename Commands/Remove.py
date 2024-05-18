import discord
import EmbedUtils
from .Util.CommandUtils import definecmd, guild_user_check, fetch_check, playing_check, channel_check
from PYMusicBot import PYMusicBot
from Player.PlayerInstance import PlayerInstance
from Player.MediaSource import MediaSource

@definecmd("remove", 
           "Removes an item from the queue")
@discord.app_commands.describe(index="The song index in the queue to remove")
async def cmd_remove(e : discord.Interaction, index : int):
    if not await guild_user_check(e): return
    client : PYMusicBot = e.client
    player : PlayerInstance | None = client.get_player(e.guild)

    if not await playing_check(e, player) or not await channel_check(e, player) or not await fetch_check(e, player):
        return

    real_index = index - 1

    if real_index < 0 or real_index >= len(player._queue):
        await e.response.send_message(embed=EmbedUtils.error(
            title="Out of range",
            description="The specified index is outside the queue's range",
            user=e.user
        ), ephemeral=True)
        return
    
    source : MediaSource = player._queue.pop(real_index)
    player.logger.info(f"Queue entry at {real_index} removed (by {e.user.id})")

    await e.response.send_message(embed=EmbedUtils.success(
        title="Queue modified",
        description=(f"Song at index {index} was removed:\n" + 
                     f"[`{source.title}`]({source.source_url})"),
        user=e.user
    ))