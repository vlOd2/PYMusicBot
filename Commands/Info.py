import discord
import Utils
from Commands.CommandHandler import CommandDeclaration, CommandHandler
from PYMusicBot import PYMusicBot
from FFmpegAudioSource import FFmpegAudioSource
from time import time

@CommandDeclaration("info", CommandHandler("Gets information on what is currently being streamed", needs_listening_executor=False))
@CommandDeclaration("nowplaying", CommandHandler("Alias for the command \"info\"", needs_listening_executor=False))
@CommandDeclaration("np", CommandHandler("Alias for the command \"info\"", needs_listening_executor=False))
async def cmd_info(instance : PYMusicBot, 
             message : discord.message.Message, 
             channel : discord.channel.TextChannel, 
             guild : discord.guild.Guild,
             args : list[str]):
    audio_source : (FFmpegAudioSource | None) = instance.get_voice_client().source

    if audio_source:
        audio_data = audio_source.data
        audio_requester = await instance.fetch_user(audio_data["__discord_user_id"])

        audio_duration = audio_data["duration"]
        audio_time_elapsed = int(time()) - audio_source.start_time if audio_duration > 0 else 0
        progress_bar_progress = audio_time_elapsed / audio_duration if audio_duration > 0 else 0

        info_embed = discord.Embed()
        info_embed.title = audio_data["title"]
        info_embed.url = audio_data["webpage_url"]
        info_embed.colour = discord.Colour.from_rgb(0, 255, 0)
        info_embed.set_thumbnail(url=(audio_data["thumbnail"] if "thumbnail" in audio_data else None))
        info_embed.set_author(name=audio_requester, icon_url=audio_requester.display_avatar)
        info_embed.set_footer(text="PYMusicBot")

        if audio_duration > 0:
            info_embed.description = f"{Utils.get_progress_bar(progress_bar_progress)} `[{Utils.get_secs_formatted(audio_time_elapsed)}/{Utils.get_secs_formatted(audio_duration)}]`"
        else:
            info_embed.description = f":red_circle: Live"

        await message.reply(embed=info_embed)
    elif instance.is_resolving:
        await message.reply(embed=Utils.get_embed(
            ":hourglass: Busy", 
            "Currently resolving a query, please wait...",
            (0, 0, 255)))
    else:
        await message.reply(embed=Utils.get_embed(
            ":information_source: Not Streaming", 
            "Nothing is being streamed right now",
            (0, 255, 0)))