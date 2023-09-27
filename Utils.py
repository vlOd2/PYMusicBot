import subprocess
import discord
import fnmatch
from datetime import datetime, timezone
from urllib.parse import urlparse

def get_video_duration(input):
    args = f"ffprobe -v quiet -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {input}"
    process = subprocess.Popen(args, shell=True, text=True, stdout=subprocess.PIPE)
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

# Convenience function for adding a reaction
async def add_reaction(message, reaction):
    try:
        await message.add_reaction(reaction)
    except:
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