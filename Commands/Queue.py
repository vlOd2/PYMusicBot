import discord
import textwrap
import Utils
from Commands.CommandHandler import CommandDeclaration, CommandHandler
from PYMusicBot import PYMusicBot
from FFmpegAudioSource import FFmpegAudioSource

@CommandDeclaration("queue", CommandHandler("Provides a list of the queue"))
async def cmd_queue(instance : PYMusicBot, 
             message : discord.message.Message, 
             channel : discord.channel.TextChannel, 
             guild : discord.guild.Guild,
             args : list[str]):
    if len(instance.music_queue) < 1:
        await message.reply(embed=Utils.get_embed(
            ":information_source: The queue is empty", 
            "There are no songs in the queue", 
            (0, 255, 0)))
        return

    page_size = 5
    pages_data = []
    page_index = int(args[0]) if len(args) > 0 and args[0].isnumeric() else 0

    # Calculate the queue pages
    for i in range(0, len(instance.music_queue), page_size): 
        pages_data.append(instance.music_queue[i:i + page_size])

    if page_index < 0 or page_index > len(pages_data) - 1:
        await message.reply(embed=Utils.get_error_embed("Page index is outside the queue range!"))
        return

    queue_message = f"📃 Queue page {page_index}/{len(pages_data) - 1}\n"

    current_audio_source : (FFmpegAudioSource | None) = instance.get_voice_client().source
    if current_audio_source:
        current_audio_data = current_audio_source.data
        queue_message += f":notes: Currently streaming [`{current_audio_data['title']}`](<{current_audio_data['webpage_url']}>)\n\n"
    else:
        queue_message += f":information_source: Nothing is being streamed right now\n\n"

    for song in pages_data[page_index]:
        requester = await instance.fetch_user(song['__discord_user_id'])
        is_flat_queue : bool = song["__is_flat_queue"]

        url = song["webpage_url"] if not is_flat_queue else song["url"]
        duration = Utils.get_secs_formatted(song['duration']) if not is_flat_queue else "-"

        queue_message += f"{instance.music_queue.index(song)}\. [{duration}]" 
        queue_message += f" [`{song['title']}`](<{url}>) - {requester.mention}\n"

    await message.reply(embed=Utils.get_embed(
        ":arrow_right_hook: Queue", 
        queue_message, 
        (0, 255, 0)), allowed_mentions=Utils.get_no_allowed_mentions())