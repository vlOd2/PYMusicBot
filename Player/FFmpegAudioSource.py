import discord

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 2",
    "options": "-vn"
}

def get_ffmpeg_audio_src(url : str) -> discord.FFmpegPCMAudio:
    return discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS)