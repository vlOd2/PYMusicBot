import asyncio
import yt_dlp
import logging
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
            "player_skip": [ "configs", "webpage", "js" ],
            "skip": [ "hls", "dash", "translated_subs" ]
        }
    },
    "noplaylist": True,
    "break_on_reject": True,
    "match_filter": match_func,
    "nocheckcertificate": True,
    "ignoreerrors": False,
    "logtostderr": True,
    "quiet": True,
    "no_warnings": True,
    "color": "always",
    "default_search": "auto",
    "source_address": "0.0.0.0"
}
YOUTUBEDL_FLAT_OPTIONS = YOUTUBEDL_OPTIONS.copy()
YOUTUBEDL_FLAT_OPTIONS["extract_flat"] = True

_youtubedl = yt_dlp.YoutubeDL(YOUTUBEDL_OPTIONS)
_flat_youtubedl = yt_dlp.YoutubeDL(YOUTUBEDL_FLAT_OPTIONS)
_warm_up_done = False

async def fetch(query) -> dict[str, Any]:
    if not _warm_up_done: raise Exception("yt-dlp warm-up has not finished!")
    data = await _fetch(query, _youtubedl)

    if "entries" in data:
        if len(data["entries"]) < 1:
            raise ValueError("Fetching yielded 0 results")
        data = data["entries"][0]

    data["duration"] = int(data["duration"]) if "duration" in data else int(ffprobe_duration(data["url"]) / 1000)
    
    if data["duration"] < 0: 
        data["duration"] = 0

    return data

async def fetch_flat(query) -> dict[str, Any]:
    if not _warm_up_done: raise Exception("yt-dlp warm-up has not finished!")
    return await _fetch(query, _flat_youtubedl)

async def _fetch(query, instance : yt_dlp.YoutubeDL) -> dict[str, Any]:
    return await asyncio.get_running_loop().run_in_executor(None, lambda: instance.extract_info(query, download=False))

async def warmup():
    global _warm_up_done
    logger = logging.getLogger("yt-dlp-warmup")
    logger.warning("Skipping warm-up because I want to fucking test")
    # logger.info("Warming up yt-dlp...")
    # for h in logger.handlers: h.flush()
    # await _fetch("Rick Roll", _youtubedl)
    # logger.info("Finished search warm-up")
    # await _fetch("https://www.youtube.com/watch?v=dQw4w9WgXcQ", _youtubedl)
    # logger.info("Finished direct URL warm-up")
    _warm_up_done = True