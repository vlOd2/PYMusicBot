import discord
import EmbedUtils
from .Util.CommandUtils import definecmd, guild_check, channel_check
from PYMusicBot import PYMusicBot
from Player.PlayerInstance import PlayerInstance
from Player.MediaSource import MediaSource
from Utils import exstr
from .NowPlaying import _get_embed

@definecmd("play", 
           "Adds something to the queue")
async def cmd_play(e : discord.Interaction, query : str = None, file : discord.Attachment = None):
    if not await guild_check(e): return
    client : PYMusicBot = e.client
    player : PlayerInstance | None = client.get_player(e.guild)
    had_to_join = False

    if query == None and file == None:
        await e.response.send_message(embed=EmbedUtils.error(
            "Bad query",
            "No valid query was specified!",
            e.user
        ), ephemeral=True)
        return

    if file != None:
        query = file.url

    if player == None and e.user.voice == None:
        await e.response.send_message(embed=EmbedUtils.error(
            "Failed to join",
            "You are not currently in a voice channel",
            e.user
        ), ephemeral=True)
        return

    if not await channel_check(e, player):
        return

    if player == None:
        try:
            player = await client.allocate_player(e.user, e.user.voice.channel, e.guild)
            had_to_join = True
        except Exception as ex:
            await e.response.send_message(embed=EmbedUtils.error(
                "Failed to join",
                f"Couldn't join the voice channel, please report this to an administrator:\n{exstr(ex)}",
                e.user
            ), ephemeral=True)
            return

    source : MediaSource
    result : bool
    try:
        await e.response.defer()
        player.logger.info(f"Fetching {e.user.name}'s ({e.user.id}) query \"{query}\"...")
        source = await MediaSource.fetch(query, e.user)
        result = player.add_queue(source)
    except Exception as ex:
        error_full = exstr(ex)
        error = ex.__str__().strip()
        if len(error) == 0: error = error_full

        await e.followup.send(embed=EmbedUtils.error(
            "Fetching failed",
            error,
            e.user
        ), ephemeral=True)
        if had_to_join: await player.stop()
        
        return

    queue_state : str 
    if result:
        queue_state = ":white_check_mark: This song has been added to the player's queue"
    else:
        queue_state = ":checkered_flag: This song has started the player"

    embed : discord.Embed = _get_embed(source)
    embed.add_field(name="** **", value=queue_state, inline=False)

    await e.followup.send(embed=embed)