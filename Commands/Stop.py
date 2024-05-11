import discord
import EmbedUtils
from .CommandDefinitions import definecmd, invoker_channel_checks
from PYMusicBot import PYMusicBot
from Player.PlayerInstance import PlayerInstance
from Utils import exstr

@definecmd("stop", 
           "Clears the queue and disconnects")
async def cmd_stop(e : discord.Interaction):
    client : PYMusicBot = e.client
    player : PlayerInstance | None = client.get_player(e.guild)

    if not await invoker_channel_checks(e, player, client):
        return

    if e.user.voice == None and player == None:
        await e.response.send_message(embed=EmbedUtils.error(
            "Failed to join",
            "You are not currently in a voice channel",
            client,
            e.user
        ), ephemeral=True)
        return

    if e.user.voice == None or e.user.voice.channel.id != player.channel.id:
        await e.response.send_message(embed=EmbedUtils.error(
            "Mismatched channel",
            "You are not currently in my voice channel",
            client,
            e.user
        ), ephemeral=True)
        return

    if player == None:
        await e.response.send_message(embed=EmbedUtils.error(
            "Not connected",
            "Not currently connected in a voice channel",
            client,
            e.user
        ))
        return

    await player.stop()
    await e.response.send_message(embed=EmbedUtils.success(
        "Player stopped",
        "The player has been stopped successfully",
        client,
        e.user
    ))