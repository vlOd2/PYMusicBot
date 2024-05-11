import discord
import EmbedUtils
from .CommandDefinitions import definecmd, invoker_channel_checks
from PYMusicBot import PYMusicBot
from Player.PlayerInstance import PlayerInstance
from Player.MediaSource import MediaSource
from Utils import exstr, formated_time

def _get_embed(source : MediaSource, 
               result : bool, 
               client : PYMusicBot, 
               user : discord.User) -> discord.Embed:
    duration = formated_time(source.duration) if source.duration != 0 else ":red_circle: Live"
    uploader = f"[{source.uploader}]({source.uploader_url})" if source.uploader != None else "N/A"
    queue_state = ":white_check_mark: Added to the queue" if result else ":notes: Now playing"

    embed = discord.Embed()
    embed.colour = EmbedUtils.Constants.EMBED_COLOR_STATE
    embed.title = source.title
    embed.url = source.source_url
    embed.add_field(name="Duration", value=duration, inline=True)
    embed.add_field(name="Uploader", value=uploader, inline=True)
    embed.add_field(name="** **", value=queue_state, inline=False)
    embed.set_thumbnail(url=source.thumbnail)
    EmbedUtils.add_fields(client, user, embed)

    return embed

@definecmd("play", 
           "Adds something to the queue")
async def cmd_play(e : discord.Interaction, query : str):
    client : PYMusicBot = e.client
    player : PlayerInstance | None = client.get_player(e.guild)

    if not await invoker_channel_checks(e, player, client):
        return

    if player == None:
        try:
            player = await client.allocate_player(e.user, e.user.voice.channel, e.guild)
        except Exception as ex:
            await e.response.send_message(embed=EmbedUtils.error(
                "Failed to join",
                f"Couldn't join the voice channel, please report this to an administrator:\n{exstr(ex)}",
                client,
                e.user
            ), ephemeral=True)
            return

    source : MediaSource
    result : bool
    try:
        await e.response.defer()
        source = await MediaSource.fetch(query, e.user)
        result = await player.add_queue(source)
    except Exception as ex:
        # This will print the exception
        exstr(ex)
        await e.followup.send(embed=EmbedUtils.error(
            "Fetching failed",
            f"Fetching operation resulted into an error: {ex}",
            client,
            e.user
        ), ephemeral=True)
        return

    await e.followup.send(embed=_get_embed(source, result, client, e.user))