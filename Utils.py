import subprocess
import discord
import fnmatch
import logging
from datetime import datetime, timezone
from urllib.parse import urlparse

def get_video_duration(input):
    logger = logging.getLogger("PYMusicBot")
    args = [ 
        "ffprobe", 
        "-v", "error", 
        "-show_entries", "format=duration", 
        "-of", "default=noprint_wrappers=1:nokey=1", 
        input 
    ]

    try:
        logger.info(f"Starting FFprobe with the following process start-up args: {args}")

        process_result = subprocess.run(args, text=True, capture_output=True)
        query_result = process_result.stdout.strip()
        logger.info(f"Raw result from FFprobe: {query_result}")

        if not query_result or len(query_result) < 1:
            logger.error(f"FFprobe has encountered an error: {process_result.stderr.strip()}")
            return -1

        if query_result == "N/A":
            logger.info("FFprobe reported the query was not applicable")
            return -1

        return int(float(query_result) * 1000)
    except Exception as ex:
        logger.error(f"Unable to run FFprobe:")
        logger.exception(ex)
        return -1

def get_secs_formatted(seconds):
    timestamp = datetime.fromtimestamp(seconds, tz=timezone.utc)
    return timestamp.strftime('%H:%M:%S') if timestamp.hour > 0 else timestamp.strftime('%M:%S')

def strip_unicode(str):
    return str.encode("ascii", "ignore").decode("ascii")

def get_progress_bar(blocks_done, size=12):
    progress_bar = ""
    currently_at_pos = int(blocks_done * size)

    for i in range(size):
        if i == currently_at_pos:
            progress_bar += ":radio_button:"
        else:
            progress_bar += "▬"
    
    return progress_bar

def get_logger_file_name():
    return datetime.now().strftime("%H-%M-%S %d.%m.%Y.log")

def get_no_allowed_mentions():
    return discord.AllowedMentions(everyone=False, users=False, roles=False, replied_user=True)

def get_embed(title, description, color):
    embed = discord.Embed()
    embed.colour = discord.Colour.from_rgb(*color)
    embed.title = title
    embed.description = description
    embed.set_footer(text="PYMusicBot")
    return embed

def get_error_embed(message):
    return get_embed(":x: Error", message, (255, 0, 0))

async def add_reaction(message : discord.message.Message, reaction):
    try:
        await message.add_reaction(reaction)
    except:
        logging.getLogger("PYMusicBot").warning(f"Failed to react to a message sent by {message.author.id}!"
                                                f" Maybe we got blocked by them?")
        pass

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False
    
def is_host_banned(host, ban_list, whitelist_mode):
    in_ban_list = any([fnmatch.fnmatch(host, entry) for entry in ban_list])

    if not whitelist_mode and in_ban_list:
        return True
    elif whitelist_mode and not in_ban_list:
        return True
    else:
        return False

def is_something_banned(entry, ban_list, whitelist_mode):
    if not whitelist_mode and entry in ban_list:
        return True
    elif whitelist_mode and entry not in ban_list:
        return True
    else:
        return False