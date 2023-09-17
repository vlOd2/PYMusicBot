import os
import sys
import logging
import Utils
from time import time
from Config import Config
from Commands import *
from PYMusicBot import PYMusicBot

def setup_logger():
    if not os.path.exists("logging"):
        os.mkdir("logging")

    logger_stream_handler = logging.StreamHandler(sys.stdout)
    logger_file_handler = logging.FileHandler(f"logging/{Utils.get_logger_file_name()}", "w")

    logger_formatter = logging.Formatter("%(asctime)s [%(levelname)s] [%(name)s] %(message)s", "%H:%M:%S")
    logger_stream_handler.setFormatter(logger_formatter)
    logger_file_handler.setFormatter(logger_formatter)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(logger_stream_handler)
    logger.addHandler(logger_file_handler)

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

def load_config():
    logger = logging.getLogger()
    config = Config()

    def create_default_config():
        logger.info("Creating default config")
        config_file = open("config.json", "w")
        config_file.write(config.export_json())
        config_file.close()

    if not os.path.exists("config.json"):
        create_default_config()
    else:
        logger.info("Loading config...")
        try:
            config_file = open("config.json", "r")
            config.import_json(config_file.read())
            config_file.close()
            logger.info(f"Loaded config")
        except Exception as ex:
            logger.warn(f"Unable to load the config: {ex}")
            os.rename("config.json", f"config_broken_{int(time() * 1000)}.json")
            create_default_config()

    if config.OPERATING_GUILD == None or config.VOICE_CHANNEL == None:
        logger.fatal("No operating guild or voice channel specified in config!")
        return

    return config

setup_logger()
instance = PYMusicBot(load_config())

logging.getLogger().info("Running PYMusicBot... To quit, press Ctrl + C")
instance.run(load_token(), log_handler=None)