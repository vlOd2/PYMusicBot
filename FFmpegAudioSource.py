import discord

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 2",
    "options": "-vn"
}

class FFmpegAudioSource(discord.PCMVolumeTransformer):
    def __init__(self, source, data, volume=1):
        super().__init__(source, volume)
        self.data = data
        self.start_time = 0

    @classmethod
    async def get_instance(clazz, data, volume=1):
        return clazz(discord.FFmpegPCMAudio(data["url"], **FFMPEG_OPTIONS), data, volume)
    
