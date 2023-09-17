import asyncio
import yt_dlp
import asyncio
from Utils import get_video_duration

def match_func(info_dict, incomplete=False):
    if "playlist" in info_dict and info_dict["playlist"] == "recommended":
        return "The playlist recommended is not allowed!"

    return None

YOUTUBEDL_OPTIONS = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "break_on_reject": True,
    "match_filter": match_func,
    "nocheckcertificate": True,
    "ignoreerrors": False,
    "logtostderr": False,
    "quiet": False,
    "no_warnings": False,
    "color": "no_color",
    "default_search": "auto",
    "source_address": "0.0.0.0"
}
YOUTUBEDL_FLAT_OPTIONS = YOUTUBEDL_OPTIONS.copy()
YOUTUBEDL_FLAT_OPTIONS["extract_flat"] = True

youtubedl = yt_dlp.YoutubeDL(YOUTUBEDL_OPTIONS)
flat_youtubedl = yt_dlp.YoutubeDL(YOUTUBEDL_FLAT_OPTIONS)

async def get_query_data(query):
    data = await asyncio.get_event_loop().run_in_executor(None, lambda: youtubedl.extract_info(query, download=False))

    if "entries" in data:
        if len(data["entries"]) < 1:
            raise ValueError("The query has returned 0 results")
        data = data["entries"][0]

    # Calculate the duration if it doesn't exist (and also round it down)
    data["duration"] = int(data["duration"]) if "duration" in data else int(get_video_duration(data["url"]) / 1000)
    
    if data["duration"] < 0: 
        data["duration"] = 0

    return data

async def get_query_raw_data(query):
    return await asyncio.get_event_loop().run_in_executor(None, lambda: youtubedl.extract_info(query, download=False))

async def get_flat_query_raw_data(query):
    return await asyncio.get_event_loop().run_in_executor(None, lambda: flat_youtubedl.extract_info(query, download=False))