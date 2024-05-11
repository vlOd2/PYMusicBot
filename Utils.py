import traceback
import logging
import subprocess
from datetime import datetime, timezone

def exstr(ex : BaseException):
    traceback.print_exception(ex)
    formated : list[str] = traceback.format_exception(ex)
    output = ""

    for t in formated:
        output += f"{t}"
    
    return output

def logger_file():
    return datetime.now().strftime("%H-%M-%S %d.%m.%Y.log")

def formated_time(seconds):
    timestamp = datetime.fromtimestamp(seconds, tz=timezone.utc)
    return timestamp.strftime('%H:%M:%S') if timestamp.hour > 0 else timestamp.strftime('%M:%S')

def ffprobe_duration(input):
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
