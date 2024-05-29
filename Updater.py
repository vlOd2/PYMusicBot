import Constants
import urllib3
import logging
import threading
from Version import Version

_HTTP = urllib3.PoolManager()

def check_for_updates():
    threading.Thread(target=_check_for_updates,daemon=True).start()

def _check_for_updates():
    logger = logging.getLogger("Updater")
    logger.info("Checking for updates...")
    latest_ver = get_latest_version()

    if latest_ver == None:
        logger.error("Failed to check for updates!")
        return
    
    if Constants.APP_VERSION != latest_ver:
        if Constants.APP_VERSION < latest_ver:
            logger.warning(f"A new version of PYMusicBot V2 is available! ({latest_ver})")
        else:
            logger.warning(f"You're version subtype is not matching the latest! " + 
                           f"You are probably on a non-stable release! (latest: {latest_ver})")
        return
    
    logger.info(f"You are on the latest version! ({latest_ver})")

def get_latest_version() -> Version | None:
    try:
        with _HTTP.request("GET", Constants.LATEST_VERSION_INFO_URL) as response:
            latest_ver_raw = response.data.decode()
        return Version.from_str(latest_ver_raw)
    except:
        return None