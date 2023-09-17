import json
from typing import Any

class Config():
    def __init__(self):
        self.OPERATING_GUILD = None
        self.VOICE_CHANNEL = None
        self.BANNED_USERS = []
        self.BANNED_ROLES = []
        self.ADMIN_USERS = []
        self.ADMIN_ROLES = []
        self.DEFAULT_VOICE_VOLUME = 1.0

    def export_json(self):
        return json.dumps(self, default=lambda obj: obj.__dict__, indent=4)

    def import_json(self, exported):
        parsed_exported : dict[str, Any] = json.loads(exported)
        for key, value in parsed_exported.items():
            self.__dict__[key] = value