import os
import sys
import logging
import Utils
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

def main():
    setup_logger()
    logging.getLogger().info("Running PYMusicBot... To quit, press Ctrl + C")
    instance = PYMusicBot()
    instance.run(load_token(), log_handler=None)

if __name__ == "__main__":
    main()