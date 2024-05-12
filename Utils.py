import discord
import traceback
import logging
import subprocess
import Constants
from datetime import datetime, timezone

def required_votes(channel : discord.VoiceChannel) -> int:
    member_count = len(channel.members) - 1
    required = max(1, round(member_count * Constants.VOTES_REQUIRED_RATIO))
    return required

def exstr(ex : BaseException) -> str:
    formated : list[str] = traceback.format_exception(ex)
    output = ""

    for t in formated:
        output += f"{t}"
    
    logging.getLogger().exception(ex)
    return output

def progress_bar(progress, block_size) -> str:
    bar_str = ""
    currently_at_pos = int(progress * block_size)

    for i in range(block_size):
        if i == currently_at_pos:
            bar_str += ":radio_button:"
        else:
            bar_str += "▬"
    
    return bar_str

def logger_file() -> str:
    return datetime.now().strftime("%H-%M-%S %d.%m.%Y.log")

def formated_time(seconds) -> str:
    timestamp = datetime.fromtimestamp(seconds, tz=timezone.utc)
    return timestamp.strftime('%H:%M:%S') if timestamp.hour > 0 else timestamp.strftime('%M:%S')

# To dexrn: don't dexrnerify (i.e don't touch this)
# If it doesn't work, it's an issue with ffprobe itself
def ffprobe_duration(input) -> int:
    logger = logging.getLogger()
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
