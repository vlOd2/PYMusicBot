import discord
from discord.ext import tasks
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
VERSION = "1.2.2"

class PYMusicBot(discord.Client):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)

        # Config
        self._is_ready = False
        self.config = Config()
        self.operating_guild : (discord.Guild | None) = None
        self.guild_member : (discord.Member | None) = None

        # Voice
        self.is_joining = False
        self.voice_channel : (discord.channel.VoiceChannel | None) = None
        self._voice_client : (discord.voice_client.VoiceClient | None) = None

        # Streamer
        self.is_resolving = False
        self.voice_volume = self.config.DEFAULT_VOICE_VOLUME
        self.music_queue : list[dict[str, Any]] = []
        self.last_song : (dict[str, Any] | None) = None
        self.repeat_last_song = False
        self.suppress_queue_stream_on_stop = False

    async def on_ready(self):
        self.logger = logging.getLogger("PYMusicBot")
        self.logger.info(f"Logged in as {self.user}")
        self.logger.info(f"You can invite the bot using the following URL: " + 
                         f"https://discord.com/oauth2/authorize?client_id={self.user.id}&permissions=274914954304&scope=bot")
        await self.load_config()
        await self.change_presence(activity=discord.activity.Game("music to you"))
        self._is_ready = True

    async def load_config(self):
        self.config.load()

        try:
            guild = await self.fetch_guild(self.config.OPERATING_GUILD)
        except:
            guild = None

        if not guild:
            self.logger.fatal("Invalid operating guild specified in config! Shutting down...")
            await self.close()
            return

        self.operating_guild = guild
        self.guild_member = await guild.fetch_member(self.user.id)
        self.logger.info(f"The bot will operate in the guild \"{guild.name}\" ({guild.id})")

    async def on_message(self, message : discord.message.Message):
        if (not self._is_ready or 
            message.author == self.user or 
            message.author.bot or 
            not isinstance(message.channel, discord.channel.TextChannel) or
            message.guild.id != self.operating_guild.id or
            Utils.is_something_banned(message.channel.id, 
                                     self.config.BANNED_TEXT_CHANNELS, 
                                     self.config.BANNED_TEXT_CHANNELS_IS_WHITELIST)):
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
                self.logger.warning(f"Banned user ({message.author}) attempted to execute a command!")
                if not self.config.NO_REPLY_TO_BANNED:
                    await message.reply(embed=
                                            Utils.get_embed(":hammer: Banned", "You are not allowed to use commands!", (255, 0, 0)))
                return

            if cmd_handler.needs_join_voice_channel and not self.get_voice_client():
                await message.reply(embed=
                                    Utils.get_error_embed("I haven't joined the voice channel!"))
                return
            
            if cmd_handler.needs_listening_executor and self.get_voice_client():
                if not message.author.voice or message.author.voice.channel.id != self.voice_channel.id:
                    await message.reply(embed=
                                        Utils.get_error_embed("You must be listening in my voice channel to execute that command!"))
                    return

            if cmd_handler.needs_admin or self.config.COMMANDS_ADMIN_ONLY:
                if not self.is_administrator(message.author):
                    await message.reply(embed=
                                        Utils.get_error_embed(
                                            "You must be an administrator to execute that command! (defined in the config)"))
                    return
                
            try:
                await cmd_handler.func(self, message, channel, guild, args)
            except Exception as ex:
                self.logger.error(f"The command \"{cmd}\" has ran into an un-handled exception:")
                self.logger.exception(ex)
                await message.reply(embed=
                                        Utils.get_error_embed(f"The command has ran into an un-handled exception: {ex}"))
        else:
            self.logger.warning(f"\"{cmd}\" is not a valid command!")
            await message.reply(embed=
                                        Utils.get_error_embed("Invalid command! Check \"help\" for a list of available commands"))

    async def stream_data_voice_channel(self, data, callback):
        if not self.get_voice_client():
            self.logger.warning("Attempted to stream, but not in the voice channel")
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
        self.last_song = data
        await callback(None)

    async def leave_voice_channel(self):
        if self._voice_client:
            self.logger.info("Leaving voice channel...")
            await self._voice_client.disconnect()
            self._voice_client.cleanup()
        self.dispose_voice()

    def get_voice_client(self) -> (discord.voice_client.VoiceClient | None):
        if not self.voice_channel and self._voice_client:
            asyncio.ensure_future(voice_client.disconnect(), loop=self.loop)
            self._voice_client = None

        if self._voice_client and not self._voice_client.is_connected():
            self._voice_client = None

        if self.voice_channel:
            voice_client = discord.utils.get(self.voice_clients, guild=self.voice_channel.guild)
            if not self._voice_client and voice_client:
                self.logger.warning("Lost track of voice client! Cleaning up...")
                asyncio.ensure_future(voice_client.disconnect(), loop=self.loop)
                voice_client.cleanup()
                voice_client = None

        if not self._voice_client:
            self.dispose_voice()

        return self._voice_client
    
    def dispose_voice(self):
        self.logger.info("Disposing voice...")
        self.logger.info("Stopping loop on_vc_check_tick...")
        self.on_vc_check_tick.stop()
        self._voice_client = None
        self.voice_channel = None
        self.last_song = None
        self.clear_music_queue()

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
                self.logger.error(f"Unable to play next item from queue:")
                self.logger.exception(ex)
                await self.stream_next_queue_item()
            finally:
                self.is_resolving = False
        else:
            self.logger.info("Nothing to stream from the queue")

    async def on_stream_end(self, error):
        self.logger.info("Streaming ended")

        if error: 
            self.logger.error(f"Streaming error: {error}")
            
        if self.repeat_last_song and self.last_song and not self.suppress_queue_stream_on_stop:
            async def stream_callback(error_msg): 
                if error_msg:
                    self.logger.error(f"Repeat last song stream callback resulted in error: {error_msg}")

            self.logger.info("Repeat is on, replaying the last song...")
            await self.stream_data_voice_channel(self.last_song, stream_callback)
        else:
            if self.repeat_last_song and self.suppress_queue_stream_on_stop:
                self.logger.info("Repeating the last song has been suppressed")
                self.suppress_queue_stream_on_stop = False

            if not self.suppress_queue_stream_on_stop:
                if self.get_voice_client(): 
                    self._voice_client.stop()
                    await self.stream_next_queue_item()
            else:
                self.logger.info("Streaming next item from the queue has been suppressed")
                self.suppress_queue_stream_on_stop = False
                return

    def clear_music_queue(self):
        self.logger.info("Clearing the music queue...")
        self.music_queue.clear()

    @tasks.loop(seconds=5)
    async def on_vc_check_tick(self):
        if not self.voice_channel: return

        if len(self.voice_channel.members) < 2:
            self.logger.warning("The VC check tick failed (we are alone in VC), leaving the voice channel...")
            await self.leave_voice_channel()