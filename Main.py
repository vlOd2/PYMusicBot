from Core import ModuleCheck
import logging
import sys
import os
import discord
from Core import Utils
from Core import PYMusicBot
from Core import Config
from Core import Constants
from Core.CustomColorFormatter import CustomColorFormatter
from Updater import Updater
from Commands import *

LOGGER_FORMAT = {
    "fmt": "%(asctime)s [%(levelname)s] [%(name)s] %(message)s", 
    "datefmt": "%H:%M:%S"
}

def setup_logger__file_logger(formatter):
    if not os.path.exists("Logs"):
        os.mkdir("Logs")

    handler = logging.FileHandler(f"Logs/{Utils.logger_file()}", "w", "utf-8")
    handler.setFormatter(formatter)
    return handler

def setup_logger():
    formatter = CustomColorFormatter()
    fallback_formatter = logging.Formatter(**LOGGER_FORMAT)

    handler = logging.StreamHandler(sys.stdout)
    if discord.utils.stream_supports_colour(handler.stream):
        handler.setFormatter(formatter)
    else:    
        handler.setFormatter(fallback_formatter)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.addHandler(setup_logger__file_logger(fallback_formatter))

def load_token():
    logger = logging.getLogger()

    if not os.path.exists("token.txt"):
        logger.fatal("token.txt doesn't exist!")
        return

    logger.info("Loading token from token.txt...")
    token_file = open("token.txt")
    token = token_file.readline()
    token_file.close()

    return token

def main():
    setup_logger()
    Config.ConfigInstance.load()
    Config.ConfigInstance.save()

    api_version = discord.version_info
    if api_version.major < 2 or api_version.minor < 4:
        logging.getLogger().fatal("Please use discord.py 2.4+")
        return

    token = load_token()
    if token == None: 
        return

    Updater.check_for_updates()
    logging.getLogger().info(f"Running PYMusicBot V2 ({Constants.APP_VERSION})... To quit, press Ctrl + C")
    instance = PYMusicBot.PYMusicBot()
    instance.run(token, log_handler=None)

if __name__ == "__main__":
    main()