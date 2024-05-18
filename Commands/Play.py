import discord
import EmbedUtils
from .Util.CommandUtils import definecmd, guild_user_check, channel_check, Config
from PYMusicBot import PYMusicBot
from Player.PlayerInstance import PlayerInstance
from Player.MediaSource import MediaSource
from Utils import exstr, url_to_host
from .NowPlaying import _get_embed

@definecmd("play", 
           "Adds something to the queue")
async def cmd_play(e : discord.Interaction, query : str = None, file : discord.Attachment = None):
    if not await guild_user_check(e): return
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
    elif file != None:
        query = file.url

    query_host = url_to_host(query)
    if query_host != None:
        # If the whitelist is actually a blacklist
        if query_host in Config.URLHostWhitelist and Config.FlipURLHostWhitelist:
            await e.response.send_message(embed=EmbedUtils.error(
                "Query blacklisted",
                f"The query's hostname (`{query_host}`) has been blacklisted",
                e.user
            ), ephemeral=True)
            return
        
        if not query_host in Config.URLHostWhitelist and not Config.FlipURLHostWhitelist:
            await e.response.send_message(embed=EmbedUtils.error(
                "Query disallowed",
                f"The query's hostname (`{query_host}`) has not been whitelisted",
                e.user
            ), ephemeral=True)
            return

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
            exstr(ex) # Log the exception
            await e.response.send_message(embed=EmbedUtils.error(
                "Failed to join",
                f"Couldn't join the voice channel:\n{ex}",
                e.user
            ), ephemeral=True)
            return

    if player.locked:
        await e.response.send_message(embed=EmbedUtils.error(
            "Player is locked",
            (f"The player is currently locked\n" + 
            f"Another play operation may be outgoing"),
            e.user
        ), ephemeral=True)
        return

    source : MediaSource
    result : bool
    try:
        player.locked = True
        await e.response.defer()
        player.logger.info(f"{e.user.name}/{e.user.id}: Fetching the query \"{query}\"")
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
    finally:
        player.locked = False

    queue_state : str 
    if result:
        queue_state = ":white_check_mark: This song has been added to the player's queue"
    else:
        queue_state = ":checkered_flag: This song has started the player"

    embed : discord.Embed = _get_embed(source)
    embed.add_field(name="** **", value=queue_state, inline=False)

    await e.followup.send(embed=embed)