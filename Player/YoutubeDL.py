import asyncio
import yt_dlp
from typing import Any
from Utils import ffprobe_duration

def match_func(info_dict, incomplete=False):
    if "playlist" in info_dict and info_dict["playlist"] == "recommended":
        return "The playlist recommended is not allowed!"

    return None

YOUTUBEDL_OPTIONS = {
    "format": "bestaudio/best",
    "check_formats": False,
    "extractor_args": {
        "youtube": {
            "player_client": [ "android_embedded" ],
            "player_skip": [ "configs", "webpage", "js" ]
        }
    },
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

_youtubedl = yt_dlp.YoutubeDL(YOUTUBEDL_OPTIONS)
_flat_youtubedl = yt_dlp.YoutubeDL(YOUTUBEDL_FLAT_OPTIONS)

async def fetch(query) -> dict[str, Any]:
    data = await fetch_raw(query)

    if "entries" in data:
        if len(data["entries"]) < 1:
            raise ValueError("Fetching yielded 0 results")
        data = data["entries"][0]

    data["duration"] = int(data["duration"]) if "duration" in data else int(ffprobe_duration(data["url"]) / 1000)
    
    if data["duration"] < 0: 
        data["duration"] = 0

    return data

async def fetch_raw(query) -> dict[str, Any]:
    return await asyncio.get_event_loop().run_in_executor(None, lambda: _youtubedl.extract_info(query, download=False))

async def fetch_flat(query) -> dict[str, Any]:
    return await asyncio.get_event_loop().run_in_executor(None, lambda: _flat_youtubedl.extract_info(query, download=False))