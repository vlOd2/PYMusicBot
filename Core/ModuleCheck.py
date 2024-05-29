import sys

# Module check
try:
    import yaml
    import discord
    import nacl
    import yt_dlp
except ModuleNotFoundError as ex:
    print("MODULE CHECK FAILED", file=sys.stderr)
    print(f"PYMusicBot was unable to locate the following module: {ex.name}", file=sys.stderr)
    print("Please make sure to install all the required dependencies before proceeding!", file=sys.stderr)
    print("\nHere is a command to install all the dependencies:", file=sys.stderr)
    print("python -m pip install git+https://github.com/Rapptz/discord.py/ PyYAML PyNaCl yt-dlp", file=sys.stderr)
    print("or", file=sys.stderr)
    print("python3 -m pip install git+https://github.com/Rapptz/discord.py/ PyYAML PyNaCl yt-dlp", file=sys.stderr)
    sys.exit() # can't specify exit code because vscode keeps bitching

# Unload modules from module check
del sys
del yaml
del discord
del nacl
del yt_dlp