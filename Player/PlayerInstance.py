# FUCKING RETARDED LANGUAGE WTF????????
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import PYMusicBot

import discord
import logging
import asyncio
from .MediaSource import MediaSource
from .FFmpegAudioSource import FFmpegAudioSource
from time import time

class PlayerInstance:
    def __init__(self, 
                invoker : discord.Member, 
                channel : discord.VoiceChannel,
                guild : discord.Guild,
                client : PYMusicBot.PYMusicBot) -> None:
        self.invoker : discord.Member = invoker
        self.channel : discord.VoiceChannel = channel
        self.guild : discord.Guild = guild
        self._client = client
        self._voice_client : discord.VoiceClient = None
        self.logger : logging.Logger = logging.getLogger(f"PlayerInstance-{guild.id}")
        self._queue : list[MediaSource] = []
        self.current_source : tuple[MediaSource, FFmpegAudioSource] = None
        self._terminating : bool = False
        self._locked : bool = False
        self.repeat : bool = False
        self._ignore_repeat : bool = False
        client.event(self.on_voice_state_update)

    async def on_voice_state_update(self, member : discord.Member, 
                                    before : discord.VoiceState, 
                                    after : discord.VoiceState):
        if self._terminating: return

        if (len(self.channel.members) - 1) < 1:
            self.logger.info("Voice state reports we are alone, disconnecting...")
            await self.stop()
            return

        if member != self._client.user: 
            return

        if after.channel == None:
            self.logger.info("Voice state reports we have been disconnected, cleaning up...")
            await self.stop()
        elif before.channel != None and before.channel.id != after.channel.id:
            self.logger.info("Voice state reports we have been moved, updating channel...")
            self.channel = after.channel

    def _play(self, source : MediaSource):
        self.logger.info(f"Now playing {source.source_url}")
        raw_source = FFmpegAudioSource.get_instance(source.url, 1)
        source.start_time = int(time())
        self.current_source = (source, raw_source)
        self._voice_client.play(raw_source, after=self._on_source_end__wrapper)

    # EQBL = Queue Ended But Locked
    async def _qebl_timeout(self):
        await asyncio.sleep(5)
        if self._locked:
            self.logger.info("QEBL: Still locked after timeout ended, quitting...")
            await self.stop()
            return
        self.logger.info("QEBL: Not locked after timeout ended")

    async def _play_queue_next(self):
        if not self._ignore_repeat:
            if self.repeat:
                self.logger.info("Repeating current song...")
                self._play(self.current_source[0])
                return            
        else:
            self.logger.info("Ignoring repeat status (probably skipped)")
            self._ignore_repeat = False

        if len(self._queue) == 0:
            if self._locked:
                self.logger.info("Queue is empty but player is locked... (QEBL)")
                self.logger.info("QEBL: Clearing current source and starting timeout")
                if self.current_source != None: self.current_source[1].cleanup()
                self.current_source = None
                asyncio.Task(self._qebl_timeout(), loop=self._client.loop)
                return
            
            self.logger.info("Queue is empty, disconnecting...")
            await self.stop()
            return
        
        self._play(self._queue.pop(0))

    def _on_source_end__wrapper(self, ex : Exception):
        # Extracted outside a funny lamda to make it more readable
        asyncio.run_coroutine_threadsafe(self._on_source_end(), self._client.loop)

    async def _on_source_end(self):
        if self._terminating: return
        self.logger.info("Playback of current source ended")
        await self._play_queue_next()

    async def start(self):
        self.logger.info(f"Connecting to {self.channel.name}/{self.channel.id}...")
        self._voice_client = await self.channel.connect(reconnect=True, self_deaf=True)

    async def stop(self, noremove = False):
        if self._terminating: return
        self.logger.info("Disconnecting...")
        self._terminating = True
        await self._voice_client.disconnect(force=True)
        if not noremove: self._client.players.remove(self)

    def skip(self):
        if self.current_source == None: return
        self.logger.info("Skipping current source...")
        self._ignore_repeat = True
        self._voice_client.stop()

    def add_queue(self, source : MediaSource) -> bool:
        if len(self._queue) == 0 and self.current_source == None:
            self._play(source)
            return False
        else:
            self._queue.append(source)
            return True

    def clear_queue(self):
        self._queue.clear()

    @property
    def locked(self) -> bool:
        return self._locked
    
    @locked.setter
    def locked(self, value : bool):
        self.logger.info(f"Setting locked state to: {value}")
        self._locked = value