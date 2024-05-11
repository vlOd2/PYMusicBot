import discord
from . import YoutubeDL

class MediaSource:
    def __init__(self) -> None:
        self.invoker : discord.Member 
        self.title : str
        self.url : str
        self.duration : int
        self.source_url : str
        self.uploader : str
        self.uploader_url : str
        self.thumbnail : str
        
    @staticmethod
    async def fetch(query : str, invoker : discord.Member):
        result = await YoutubeDL.fetch(query)
        src = MediaSource()
        src.invoker = invoker
        src.title = result["title"]
        src.url = result["url"]
        src.duration = result["duration"]
        src.source_url = result["webpage_url"]
        src.uploader = result["uploader_id"] if "uploader_id" in result else None
        src.uploader_url = result["uploader_url"] if "uploader_url" in result else None
        src.thumbnail = result["thumbnail"] if "thumbnail" in result else None
        return src