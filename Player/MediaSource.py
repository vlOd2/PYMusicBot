import discord
from . import YoutubeDL
from time import time

class MediaSource:
    def __init__(self) -> None:
        self.invoker : discord.Member 
        self.title : str
        self.url : str
        self.duration : int
        self.start_time : int
        self.source_url : str
        self.uploader : str
        self.uploader_url : str
        self.thumbnail : str
        
    @property
    def elapsed(self) -> int:
        return int(time()) - self.start_time if self.duration > 0 and self.start_time > 0 else -1

    @staticmethod
    async def fetch(query : str, invoker : discord.Member):
        result = await YoutubeDL.fetch(query)
        src = MediaSource()
        src.invoker = invoker
        src.title = result["title"]
        src.url = result["url"]
        src.duration = result["duration"]
        src.start_time = 0
        src.source_url = result["webpage_url"]
        src.uploader = result["uploader_id"] if "uploader_id" in result else None
        src.uploader_url = result["uploader_url"] if "uploader_url" in result else None
        src.thumbnail = result["thumbnail"] if "thumbnail" in result else None
        return src