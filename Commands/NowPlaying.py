import discord
import EmbedUtils
from .CommandDefinitions import definecmd, fetch_check, playing_check
from PYMusicBot import PYMusicBot
from Player.PlayerInstance import PlayerInstance
from Player.MediaSource import MediaSource
from Utils import formated_time, progress_bar

def _get_embed(source : MediaSource) -> discord.Embed:
    duration = formated_time(source.duration) if source.duration != 0 else ":red_circle: Live"
    uploader = f"[{source.uploader}]({source.uploader_url})" if source.uploader != None else "N/A"

    embed = discord.Embed()
    embed.colour = EmbedUtils.Constants.EMBED_COLOR_STATE
    embed.title = source.title
    embed.url = source.source_url
    embed.add_field(name="Uploader", value=uploader, inline=True)
    embed.add_field(name="Duration", value=duration, inline=True)
    embed.set_thumbnail(url=source.thumbnail)
    EmbedUtils.add_fields(source.invoker, embed)

    return embed

@definecmd("nowplaying", 
           "Shows the currently playing song")
async def cmd_nowplaying(e : discord.Interaction):
    client : PYMusicBot = e.client
    player : PlayerInstance | None = client.get_player(e.guild)

    if not await playing_check(e, player) or not await fetch_check(e, player):
        return

    source : MediaSource = player.current_source[0]
    elapsed : int = source.elapsed
    progress : int = elapsed / source.duration if source.duration > 0 else 0

    embed : discord.Embed = _get_embed(source)
    if source.duration > 0 and elapsed >= 0:
        embed.add_field(name="Elapsed", value=formated_time(elapsed), inline=True)
        embed.add_field(name="** **", value=progress_bar(progress, 20), inline=False)
    else:
        embed.add_field(name="Elapsed", value="N/A", inline=True)

    await e.response.send_message(embed=embed, ephemeral=True)