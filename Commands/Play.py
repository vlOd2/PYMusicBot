import asyncio
import discord
from Core import EmbedUtils, Constants
from Core.PYMusicBot import PYMusicBot
from Core.Utils import exstr, url_to_host, matches_in_list
from .Util.CommandUtils import definecmd, guild_user_check, channel_check, Config
from Player.PlayerInstance import PlayerInstance
from Player.MediaSource import MediaSource
from .NowPlaying import _get_embed

async def _perform_host_checks(query_host : str, e : discord.Interaction) -> bool:
    if query_host == None: return True
    matching = matches_in_list(query_host, Config.URLHostWhitelist)

    if matching and Config.FlipURLHostWhitelist: # If the whitelist is actually a blacklist
        await e.response.send_message(embed=EmbedUtils.error(
            "Query blacklisted",
            f"The query's hostname (`{query_host}`) has been blacklisted",
            e.user
        ), ephemeral=True)
        return False

    if not matching and not Config.FlipURLHostWhitelist:
        await e.response.send_message(embed=EmbedUtils.error(
            "Query disallowed",
            f"The query's hostname (`{query_host}`) has not been whitelisted",
            e.user
        ), ephemeral=True)
        return False
    
    return True

# TODO: A bit messy
@definecmd("play", 
           "Adds something to the queue")
@discord.app_commands.describe(query="The query/URL to play")
@discord.app_commands.describe(file="The file to play")
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
    if not await _perform_host_checks(query_host, e): 
        return

    if not await channel_check(e, player):
        return

    if player == None and e.user.voice == None:
        await e.response.send_message(embed=EmbedUtils.error(
            "Failed to join",
            "You are not currently in a voice channel",
            e.user
        ), ephemeral=True)
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

    async def fetch_error(error : str):
        await e.followup.send(embed=EmbedUtils.error(
            "Fetching failed",
            error,
            e.user
        ), ephemeral=True)

        if had_to_join: 
            await player.stop()

    try:
        player.locked = True
        player.logger.info(f"{e.user.name}/{e.user.id}: Fetching the query \"{query}\"")
        await e.response.defer()

        async def fetch_completed(task : asyncio.Task[MediaSource]):
            if task.cancelled() or task.exception() != None:
                return
            source : MediaSource = task.result()
            result : bool = player.add_queue(source)

            queue_state : str 
            if result:
                queue_state = ":white_check_mark: This song has been added to the player's queue"
            else:
                queue_state = ":checkered_flag: This song has started the player"

            embed : discord.Embed = _get_embed(source)
            embed.add_field(name="** **", value=queue_state, inline=False)

            await e.followup.send(embed=embed)

        fetch_task = client.loop.create_task(MediaSource.fetch(query, e.user))
        fetch_task.add_done_callback(lambda _task: client.loop.create_task(fetch_completed(_task)))
        try:
            await asyncio.wait_for(fetch_task, Constants.FETCH_TIMEOUT)
        except TimeoutError as ex:
            player.logger.warning(f"Timed out whilst fetching: {query}")
            await fetch_error(f"Failed to fetch within {Constants.FETCH_TIMEOUT} seconds. Please try again.")

    except Exception as ex:
        error_full = exstr(ex)
        error = ex.__str__().strip()
        if len(error) == 0: error = error_full
        await fetch_error(error)
    finally:
        player.locked = False