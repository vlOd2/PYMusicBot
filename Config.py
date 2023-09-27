import json
import logging
import os
from typing import Any
from time import time

class Config():
    def __init__(self):
        self.OPERATING_GUILD = None
        self.DEFAULT_VOICE_VOLUME = 1.0
        self.BANNED_USERS = []
        self.BANNED_ROLES = []
        self.NO_REPLY_TO_BANNED = False
        self.ADMIN_USERS = []
        self.ADMIN_ROLES = []
        self.COMMANDS_ADMIN_ONLY = False
        self.BANNED_TEXT_CHANNELS = []
        self.BANNED_TEXT_CHANNELS_IS_WHITELIST = False
        self.BANNED_VOICE_CHANNELS = []
        self.BANNED_VOICE_CHANNELS_IS_WHITELIST = False
        self.BANNED_STREAM_HOSTNAMES = [
            "cdn.discordapp.com",
            "youtube.com",
            "*.youtube.com",
            "tiktok.com",
            "*.tiktok.com"
        ]
        self.BANNED_STREAM_HOSTNAMES_IS_WHITELIST = True

    def export_json(self):
        return json.dumps(self, default=lambda obj: obj.__dict__, indent=4)

    def import_json(self, exported):
        parsed_exported : dict[str, Any] = json.loads(exported)
        for key, value in parsed_exported.items():
            self.__dict__[key] = value

    @classmethod
    def _create_default_config(clazz):
        logger = logging.getLogger("PYMusicBot")
        logger.info("Creating default config")
        config_file = open("config.json", "w")
        config_file.write(clazz().export_json())
        config_file.close()

    def load(self):
        logger = logging.getLogger("PYMusicBot")

        if not os.path.exists("config.json"):
            Config._create_default_config()
        else:
            logger.info("Loading config...")
            try:
                # I don't really like using "with" but less jank in the exception handling
                with open("config.json", "r+") as config_file:
                    self.import_json(config_file.read())
                    config_file.seek(0)
                    config_file.write(self.export_json())
                    config_file.truncate()
                logger.info(f"Loaded config")
            except Exception as ex:
                logger.warning(f"Unable to load the config:")
                logger.exception(ex)
                os.rename("config.json", f"config_broken_{int(time() * 1000)}.json")
                Config._create_default_config()

    def save(self):
        logger = logging.getLogger("PYMusicBot")
        logger.info("Saving config...")

        try:
            with open("config.json", "w") as config_file:
                config_file.write(self.export_json())
            logger.info(f"Saved config")
        except Exception as ex:
            logger.warning(f"Unable to save the config:")
            logger.exception(ex)