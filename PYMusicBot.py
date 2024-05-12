import discord
import logging
from Player.PlayerInstance import PlayerInstance
from Commands.CommandDefinitions import DefinedCommands
from Config import ConfigInstance as Config

class PYMusicBot(discord.Client):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(intents=intents)
        self.tree : discord.app_commands.CommandTree = discord.app_commands.CommandTree(self)
        self.players : list[PlayerInstance] = []

        # Register the slash commands
        for cmd in DefinedCommands: 
            self.tree.add_command(cmd)

    async def on_ready(self):
        await self.tree.sync()
        await self.change_presence(activity=discord.Game(Config.PresenceText))

    async def destroy_players(self):
        logging.getLogger().warning("Destroying all player instances!")
        for player in self.players:
            player.stop(True)
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

        # TODO: Add restriction checks on the invoker
        # TODO: Add restriction checks on the channel
        perms = channel.permissions_for(guild.get_member(self.user.id))

        if not perms.connect or not perms.speak:
            raise Exception("Not enough permissions to join")

        player = PlayerInstance(invoker, channel, guild, self)
        await player.start()
        self.players.append(player)

        return player