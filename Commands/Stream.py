from typing import Any
import discord
import Utils
import YoutubeDL
from urllib.parse import urlparse
from Commands.CommandHandler import CommandDeclaration, CommandHandler
from PYMusicBot import PYMusicBot

@CommandDeclaration("stream", CommandHandler("Streams the specified query (can be a link or a search query)"))
@CommandDeclaration("play", CommandHandler("Alias for the command \"stream\""))
async def cmd_stream(instance : PYMusicBot, 
             message : discord.message.Message, 
             channel : discord.channel.TextChannel, 
             guild : discord.guild.Guild,
             args : list[str]):
    if len(args) < 1:
        await message.reply(embed=Utils.get_error_embed("No query specified!"))
        return

    if instance.is_resolving:
        await message.reply(embed=Utils.get_error_embed("Cannot resolve for another query when already resolving"))
        return

    query = " ".join(args)
    instance.logger.info(f"Getting data for query \"{query}\"...")
    stream_msg = await message.reply(embed=Utils.get_embed(":hourglass: Resolving Query", 
                                                           f"Resolving the query `{query}`, please wait, this might take a while...", 
                                                           (0, 0, 255)))

    async def stream_callback(error_msg):
        if error_msg:
            await stream_msg.edit(embed=Utils.get_error_embed(f"An error has occured: {error_msg}"))
        else:
            stream_data = instance.get_voice_client().source.data
            await stream_msg.edit(embed=Utils.get_embed(
                ":notes: Now Streaming",
                f"Now streaming [`{stream_data['title']}`]({stream_data['webpage_url']}) (duration: {Utils.get_secs_formatted(stream_data['duration'])})",
                (0, 255, 0)))

    try:
        instance.is_resolving = True

        instance.logger.info("Checking if query is an URL...")
        if Utils.is_valid_url(query):
            instance.logger.info("Query is an URL, checking if the hostname is banned...")
            query_as_url = urlparse(query)
            query_as_host = f"{query_as_url.hostname}{f':{query_as_url.port}' if query_as_url.port else ''}"
            if Utils.is_host_banned(query_as_host, 
                                    instance.config.WHITELIST_STREAM_HOSTNAMES, 
                                    not instance.config.WHITELIST_IS_BLACKLIST):
                instance.logger.warning(f"Attempted to stream from banned hostname: {query_as_host}")
                await stream_msg.edit(embed=Utils.get_error_embed("The specified hostname is not allowed to be streamed from"))
                return
            instance.logger.info("Hostname was not banned, continuing...")

        instance.logger.info("Getting flat data first for query to know if it is a playlist...")
        flat_stream_data = await YoutubeDL.get_flat_query_raw_data(query)
        flat_stream_data_length = len(flat_stream_data["entries"]) if "entries" in flat_stream_data else 0
        stream_data = None

        # Check if the provided query is a playlist
        if flat_stream_data_length > 1:
            instance.logger.info("Query is a playlist, adding entries to queue...")

            flat_stream_data_entries : list[dict[str, Any]] = flat_stream_data["entries"]
            items_added = 0

            i = 0
            while i < len(flat_stream_data_entries):
                entry = flat_stream_data_entries[i]

                if i == 0:
                    try:
                        instance.logger.info("Using first entry as play target")
                        stream_data = await YoutubeDL.get_query_data(entry["url"])
                    except Exception as ex:
                        instance.logger.error(f"Attempting to resolve first entry failed, trying next one as first: {ex}")
                        flat_stream_data_entries.remove(entry)
                        continue
                else:
                    entry["__discord_user_id"] = message.author.id
                    entry["__is_flat_queue"] = True
                    instance.music_queue.append(entry)
                    instance.logger.info(f"Added \"{entry['url']}\" to the queue")
                    items_added += 1

                i += 1
            
            if not stream_data:
                raise Exception("No valid video found in the specified playlist")
            
            if items_added > 0:
                await message.reply(embed=Utils.get_embed(
                    ":white_check_mark: Queue Modified", 
                    f"Added {items_added} playlist items to the queue",
                    (0, 255, 0)))
        else:
            instance.logger.info("Query is not a playlist")
            stream_data = await YoutubeDL.get_query_data(query)

        stream_data["__discord_user_id"] = message.author.id
        stream_data["__is_flat_queue"] = False
    except Exception as ex:
        await stream_callback(str(ex))
        return
    finally:
        instance.is_resolving = False

    if instance.get_voice_client().source:
        instance.music_queue.append(stream_data)
        instance.logger.info(f"Added \"{stream_data['url']}\" to the queue")
        await stream_msg.edit(embed=Utils.get_embed(
            ":white_check_mark: Queue Modified",
            f"Added [`{stream_data['title']}`]({stream_data['webpage_url']}) to the queue (duration: {Utils.get_secs_formatted(stream_data['duration'])})", 
            (0, 255, 0)))
        return

    await instance.stream_data_voice_channel(stream_data, stream_callback)