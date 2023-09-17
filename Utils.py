import subprocess
import discord
from datetime import datetime, timezone

def get_video_duration(input):
    args = f"ffprobe -v quiet -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {input}"
    process = subprocess.Popen(args, text=True, stdout=subprocess.PIPE)
    ffprobe_result = process.stdout.readline().strip()
    process.kill()

    if not ffprobe_result or len(ffprobe_result) < 1:
        return -1
    
    try:
        return int(float(ffprobe_result) * 1000)
    except:
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