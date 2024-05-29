import discord
import logging
from Player import YoutubeDL
from Player.PlayerInstance import PlayerInstance
from Commands.Util.CommandUtils import DefinedCommands
from Config import ConfigInstance as Config
from time import time

_DEBUG_NO_TREE_SYNC = False

class PYMusicBot(discord.Client):
    tree : discord.app_commands.CommandTree
    players : list[PlayerInstance]
    logger : logging.Logger
    start_time : int

    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(intents=intents)
        self.tree = discord.app_commands.CommandTree(self)
        self.players = []
        self.logger = logging.getLogger()
        self.start_time = int(time())

        # Register the slash commands
        for cmd in DefinedCommands: 
            self.tree.add_command(cmd)

    async def _load_presence(self):
        await self.change_presence(activity=discord.Game(Config.PresenceText), status=None)

    async def on_ready(self):
        if _DEBUG_NO_TREE_SYNC:
            self.logger.error("DON'T FUCKING FORGET TO RE-ENABLE SLASH COMMANDS TREE!!!")
        else:
            self.logger.info("Synchronizing slash commands tree...")
            await self.tree.sync()
            self.logger.info("Synchronized slash commands tree")
        YoutubeDL.load_extractors(Config.YTDLPExtractors)
        await self._load_presence()
        self.logger.info("Ready! Waiting for commands...")

    async def reload_config(self):
        self.logger.info("Reloading config...")
        Config.save()
        Config.load()
        await self._load_presence()
        self.logger.info("Reloaded config")

    async def destroy_players(self):
        self.logger.warning("Destroying all player instances!")
        for player in self.players:
            await player.stop(True)
        self.players.clear()

    def get_player(self, guild : discord.Guild) -> PlayerInstance | None:
        for player in self.players:
            if player.guild.id == guild.id:
                return player
        return None

    async def allocate_player(self, 
                              invoker : discord.Member, 
                              channel : discord.VoiceChannel, 
                              guild : discord.Guild) -> PlayerInstance:
        if self.get_player(guild) != None:
            raise Exception("Player already allocated, use get_player")

        perms = channel.permissions_for(guild.get_member(self.user.id))
        if not perms.connect or not perms.speak: 
            raise Exception("Insufficient permissions to join")
        elif channel.id in Config.BannedChannels: 
            raise Exception("Channel has been blacklisted")

        self.logger.info(f"{invoker.name}/{invoker.id}: Allocating player for {guild.name}/{guild.id}")
        player = PlayerInstance(invoker, channel, guild, self)
        await player.start()
        self.players.append(player)

        return player