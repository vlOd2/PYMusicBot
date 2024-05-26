import discord

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 2",
    "options": "-vn"
}

class FFmpegAudioSource(discord.PCMVolumeTransformer):
    def __init__(self, source, volume=1):
        super().__init__(source, volume)
        self.start_time : int = 0

    @classmethod
    def get_instance(cls, url, volume=1):
        return cls(discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS), volume)
    
