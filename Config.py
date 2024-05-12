import yaml
import os
import logging
import Constants
from typing import Any

# !!! WARNING !!!
# DO NOT MODIFY THIS FILE FOR CONFIGURATION
# INSTEAD, RUN THE BOT AND EDIT "config.yml"
# YOU HAVE BEEN WARNED !!!

# !!! WARNING !!!
# DO NOT MODIFY THIS FILE FOR CONFIGURATION
# INSTEAD, RUN THE BOT AND EDIT "config.yml"
# YOU HAVE BEEN WARNED !!!

# !!! WARNING !!!
# DO NOT MODIFY THIS FILE FOR CONFIGURATION
# INSTEAD, RUN THE BOT AND EDIT "config.yml"
# YOU HAVE BEEN WARNED !!!

# !!! WARNING !!!
# DO NOT MODIFY THIS FILE FOR CONFIGURATION
# INSTEAD, RUN THE BOT AND EDIT "config.yml"
# YOU HAVE BEEN WARNED !!!

# !!! WARNING !!!
# DO NOT MODIFY THIS FILE FOR CONFIGURATION
# INSTEAD, RUN THE BOT AND EDIT "config.yml"
# YOU HAVE BEEN WARNED !!!

class _CONFIG:
    def __init__(self) -> None:
        self.PresenceText : str = "Playing music to you!"

    def _get_logger(self):
        return logging.getLogger("Configuration")

    def load(self):
        if not os.path.exists(Constants.CONFIG_FILE_NAME):
            self._get_logger().warning("Config doesn't exist, creating default...")
            self.save()
            return
        self._get_logger().info("Loading config...")

        config_file = open(Constants.CONFIG_FILE_NAME, "r")
        loaded : dict[str, Any] = yaml.safe_load(config_file)
        config_file.close()

        for key, value in loaded.items():
            self.__dict__[key] = value

    def save(self):
        self._get_logger().info("Saving config...")
        config_file = open(Constants.CONFIG_FILE_NAME, "w")
        yaml.safe_dump(self.__dict__, config_file)
        config_file.flush()
        config_file.close()

ConfigInstance = _CONFIG()