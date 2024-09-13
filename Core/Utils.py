import math
import traceback
import logging
import subprocess
import fnmatch
import datetime
from . import Constants
from urllib.parse import urlparse, urljoin

# To dexrn: don't dexrnerify (i.e don't touch this)
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
            logger.info("FFprobe reported that the query was not applicable")
            return 0

        result = int(float(query_result) * 1000)
        if result < 0:
            logger.warning("FFprobe reported a negative duration?")
            return -1

        return result
    except Exception as ex:
        logger.error(f"Unable to run FFprobe:")
        logger.exception(ex)
        return -1

def required_votes(member_count, source_duration) -> int:
    # TODO: Probably not the best way to calculate the amount of required votes
    duration_votes = 0
    if source_duration > 0:
        duration_votes = min(4, math.floor(math.sqrt(source_duration // math.log(60)) * 0.25) / 10) / 10
    required = max(1, round(member_count * (Constants.VOTE_BASE_RATIO - duration_votes)))
    return required

def url_to_host(url : str) -> str:
    try:
        parse = urlparse(urljoin(url, "/"), scheme="http")

        if not (all([parse.scheme, parse.netloc, parse.path]) and len(parse.netloc.split(".")) > 1):
            return None

        return parse.netloc
    except:
        return None

def matches_in_list(str : str, list : list[str]) -> bool:
    return any([fnmatch.fnmatch(str, entry) for entry in list])

def friendly_str_to_bool(s : str) -> bool:
    return s.lower() in [ "true", "yes", "1", "on" ]

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
    return datetime.datetime.now().strftime("%H-%M-%S %d.%m.%Y.log")

def formated_time(timestamp : int) -> str:
    seconds = timestamp % 60
    minutes = timestamp // 60 % 60
    hours = timestamp // 60 // 60 % 24
    days = timestamp // 60 // 60 // 24

    time_str = ""
    if days > 0: time_str += f"{days}:"
    if hours > 0: time_str += f"{hours}:"
    time_str += f"{minutes:02d}:{seconds:02d}"

    return time_str

def utcnow_with_delta(td : datetime.timedelta) -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC) + td