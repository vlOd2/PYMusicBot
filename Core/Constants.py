from Updater.Version import Version

# Constant values that never change
# You can change these if you want, but it's not recommended

# Fundamental
APP_VERSION = Version(2, 0, 2)
CONFIG_FILE_NAME = "config.yml"
LATEST_VERSION_INFO_URL = "https://raw.githubusercontent.com/vlOd2/PYMusicBot/main/LatestVersion.info"

# Embeds
EMBED_COLOR_SUCCESS = 0x00FF06
EMBED_COLOR_ERROR = 0xFF0000
EMBED_COLOR_STATE = 0x00ACFF
EMBED_FOOTER = "PYMusicBot V2"

# Queue
QUEUE_VIEW_TIMEOUT = 10
QUEUE_ENTRIES_PER_PAGE = 8
NOW_PLAYING_BAR_SIZE = 15
FETCH_TIMEOUT = 15

# Votes
VOTE_TIMEOUT = 30
VOTE_BASE_RATIO = 0.50
VOTE_THRESHOLD = 2