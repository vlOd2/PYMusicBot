import asyncio
import yt_dlp
import logging
from typing import Any
from Core.Utils import ffprobe_duration

def match_func(info_dict, incomplete=False):
    if "playlist" in info_dict and info_dict["playlist"] == "recommended":
        return "The playlist recommended is not allowed!"

    return None

YOUTUBEDL_OPTIONS = {
    "allowed_extractors": "",
    "format": "bestaudio/best",
    "check_formats": False,
    "extractor_args": { # Appears to be very fast and reliable
        "youtube": {
            "player_client": [ "android_embedded" ],
            "player_skip": [ "configs", "webpage", "js" ],
            "skip": [ "translated_subs" ]
        }
    },
    "noplaylist": True,
    "break_on_reject": True,
    "match_filter": match_func,
    "nocheckcertificate": True,
    "ignoreerrors": False,
    "quiet": True,
    #"verbose": False,
    "no_warnings": True,
    "color": "never",
    "default_search": "auto",
    "source_address": "0.0.0.0"
}
FETCH_TIMEOUT = 60

_youtubedl = yt_dlp.YoutubeDL(YOUTUBEDL_OPTIONS, auto_init=False)
_finished_loading = False

async def fetch(query : str) -> dict[str, Any]:
    if not _finished_loading: raise Exception("Extractors haven't been loaded!")
    data = await _fetch(query, True)

    if "entries" in data:
        if len(data["entries"]) < 1:
            raise ValueError("Fetching yielded 0 results")
        data = data["entries"][0]

    data["duration"] = int(data["duration"]) if "duration" in data else int(ffprobe_duration(data["url"]) / 1000)
    
    if data["duration"] < 0: 
        data["duration"] = 0

    return data

async def fetch_flat(query : str) -> dict[str, Any]:
    if not _finished_loading: raise Exception("Extractors haven't been loaded!")
    return await _fetch(query, False)

async def _fetch(query : str, process : bool) -> dict[str, Any]:
    future = asyncio.get_running_loop().run_in_executor(None, lambda: _youtubedl.extract_info(query, download=False, process=process))
    return await asyncio.wait_for(future, FETCH_TIMEOUT)

def load_extractors(extractor_ids : list[str]):
    global _finished_loading
    logger = logging.getLogger("yt-dlp-preload")
    logger.info("Loading yt-dlp extractors...")

    for extractor_id in extractor_ids:
        logger.info(f"Loading extractor \"{extractor_id}\"...")
        _youtubedl.get_info_extractor(extractor_id)

    logger.info("Loaded yt-dlp extractors")
    _finished_loading = True