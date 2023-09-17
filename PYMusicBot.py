import discord
import logging
import asyncio
import YoutubeDL
import Utils
from Config import Config
from Commands.CommandHandler import REGISTERED_CMDS, CommandHandler
from FFmpegAudioSource import FFmpegAudioSource
from typing import Any
from time import time

COMMAND_PREFIX = "-"

class PYMusicBot(discord.Client):
    def __init__(self, config : Config) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)

        self.config : Config = config
        self.voice_channel : (discord.channel.VoiceChannel | None) = None
        self._voice_client : (discord.voice_client.VoiceClient | None) = None
        self.voice_volume = self.config.DEFAULT_VOICE_VOLUME
        self.music_queue : list[dict[str, Any]] = []
        self.is_resolving = False
        self.suppress_queue_stream_on_stop = False

    async def on_ready(self):
        self.logger = logging.getLogger("PYMusicBot")
        self.logger.info(f"Logged in as {self.user}")
        self.logger.info(f"You can invite the bot using the following URL: " + 
                         f"https://discord.com/oauth2/authorize?client_id={self.user.id}&permissions=274914954304&scope=bot")
        
        try:
            guild = await self.fetch_guild(self.config.OPERATING_GUILD)
        except:
            guild = None
        if not guild:
            self.logger.fatal("Invalid operating guild specified in config!")
            await self.close()
            return
        
        try:
            channel = await guild.fetch_channel(self.config.VOICE_CHANNEL)
        except:
            guild = None
        if not channel or not isinstance(channel, discord.channel.VoiceChannel):
            self.logger.fatal("Invalid voice channel specified in config!")
            await self.close()
            return
        
        self.voice_channel = channel
        self.logger.info(f"Guild: {guild.name} ({guild.id})")
        self.logger.info(f"Voice channel: {self.voice_channel.name} ({self.voice_channel.id})")

        await self.change_presence(activity=discord.activity.Game("music to you"))

    async def on_message(self, message : discord.message.Message):
        if message.author == self.user or message.author.bot or not isinstance(message.channel, discord.channel.TextChannel):
            return

        message_content = message.content
        if message_content.startswith(COMMAND_PREFIX):
            content_parsed = message_content.split(" ")
            cmd = content_parsed[0].removeprefix(COMMAND_PREFIX)
            cmd_args = content_parsed[1:]
            await self.on_command(message, message.channel, message.guild, cmd, cmd_args)

    async def on_command(self, 
                         message : discord.message.Message, 
                         channel : discord.channel.TextChannel, 
                         guild : discord.guild.Guild, 
                         cmd : str, 
                         args : list[str]):
        cmd_handler : CommandHandler = REGISTERED_CMDS.get(cmd)
        self.logger.info(f"Received command \"{cmd}\" ({','.join(args)}) from {message.author}")

        if cmd_handler:
            self.logger.info(f"Executing handler for commnad \"{cmd}\"...")

            if self.is_banned(message.author) and not self.is_administrator(message.author):
                self.logger.warn(f"Banned user ({message.author}) attempted to execute a command!")
                await message.reply(embed=
                                        Utils.get_embed(":hammer: Banned", "You are not allowed to use commands!", (255, 0, 0)))
                return

            if cmd_handler.needs_join_voice_channel:
                if not self.get_voice_client():
                    await message.reply(embed=
                                        Utils.get_error_embed("I haven't joined the voice channel!"))
                    return

            if cmd_handler.needs_same_guild:
                if guild.id != self.voice_channel.guild.id:
                    await message.reply(embed=
                                        Utils.get_error_embed("The current guild doesn't match the guild of the voice channel"))
                    return

            if cmd_handler.needs_listening_executor:
                if not message.author.voice or message.author.voice.channel.id != self.voice_channel.id:
                    await message.reply(embed=
                                        Utils.get_error_embed("You must be listening in my voice channel to execute that command!"))
                    return

            if cmd_handler.needs_admin:
                if not self.is_administrator(message.author):
                    await message.reply(embed=
                                        Utils.get_error_embed(
                                            "You must be an administrator to execute that command! (defined in the config)"))
                    return

            #if not self.is_administrator(message.author):
            #    await message.reply(embed=
            #                            Utils.get_embed(
            #                                ":construction: Bot under construction",
            #                                "Bot under construction, commands only available to administrators",
            #                                (255, 72, 0)))
            #    return

            try:
                await cmd_handler.func(self, message, channel, guild, args)
            except Exception as ex:
                self.logger.error(f"The command \"{cmd}\" has ran into an un-handled exception:")
                self.logger.exception(ex)
                await message.reply(embed=
                                        Utils.get_error_embed(f"The command has ran into an un-handled exception: {ex}"))
        else:
            self.logger.warn(f"\"{cmd}\" is not a valid command!")
            await message.reply(embed=
                                        Utils.get_error_embed("Invalid command! Check \"help\" for a list of available commands"))

    async def stream_data_voice_channel(self, data, callback):
        if not self.get_voice_client():
            self.logger.warn("Attempted to stream, but not in the voice channel")
            await callback("Not in a voice channel")
            return
        
        try:
            audio_source = await FFmpegAudioSource.get_instance(data, self.voice_volume)
        except Exception as ex:
            await callback(str(ex))
            return
        
        self.get_voice_client().stop()
        self.get_voice_client().play(audio_source, after=lambda e:
                                     asyncio.run_coroutine_threadsafe(self.on_stream_end(e), self.loop))
        audio_source.start_time = int(time())

        self.logger.info(f"Now streaming audio from \"{audio_source.data['url']}\"" + 
                         f" (start time: {audio_source.start_time}, duration: {audio_source.data['duration']})")
        await callback(None)

    async def leave_voice_channel(self):
        if self._voice_client:
            self.logger.info(f"Leaving voice channel...")
            await self._voice_client.disconnect()
        self._voice_client = None

    def get_voice_client(self) -> (discord.voice_client.VoiceClient | None):
        if self._voice_client and not self._voice_client.is_connected():
            self._voice_client = None
        return self._voice_client
    
    def is_banned(self, user : discord.Member):
        if user.id in self.config.BANNED_USERS:
            return True
        
        for role in user.roles:
            if role.id in self.config.BANNED_ROLES:
                return True

        return False

    def is_administrator(self, user : discord.Member):
        if user.id in self.config.ADMIN_USERS:
            return True
        
        for role in user.roles:
            if role.id in self.config.ADMIN_ROLES:
                return True
            
        return False
    
    async def stream_next_queue_item(self):
        self.logger.info("Getting next item from queue...")

        if (len(self.music_queue) > 0):
            async def stream_callback(error_msg): 
                if error_msg:
                    self.logger.error(f"Next queue item stream callback resulted in error: {error_msg}")
            self.is_resolving = True
            audio_data = self.music_queue.pop(0)

            try:
                if audio_data["__is_flat_queue"]:
                    discord_user_id = audio_data["__discord_user_id"]
                    is_flat_queue = audio_data["__is_flat_queue"]
                    audio_data = await YoutubeDL.get_query_data(audio_data["url"])
                    audio_data["__discord_user_id"] = discord_user_id
                    audio_data["__is_flat_queue"] = is_flat_queue
                    
                await self.stream_data_voice_channel(audio_data, stream_callback)
            except Exception as ex:
                self.logger.error(f"Unable to play next item from queue: {ex}")
                await self.stream_next_queue_item()
            finally:
                self.is_resolving = False
        else:
            self.logger.info("Nothing to stream from the queue")

    async def on_stream_end(self, error):
        self.logger.info("Streaming ended")

        if error: 
            self.logger.error(f"Streaming error: {error}")

        if not self.suppress_queue_stream_on_stop:
            if self.get_voice_client(): 
                self._voice_client.stop()

            if self.get_voice_client(): 
                await self.stream_next_queue_item()
        else:
            self.logger.info("Streaming next item from the queue has been suppressed")
            self.suppress_queue_stream_on_stop = False