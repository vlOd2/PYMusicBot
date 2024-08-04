# FUCKING RETARDED LANGUAGE WTF????????
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import Core.PYMusicBot

import discord
import logging
import asyncio
from .MediaSource import MediaSource
from .FFMpegAudioSource import get_ffmpeg_audio_src
from time import time
from .VotingView import stop_all_votes

class PlayerInstance:
    invoker : discord.Member
    channel : discord.VoiceChannel
    guild : discord.Guild
    _client : Core.PYMusicBot.PYMusicBot
    _voice_client : discord.VoiceClient
    logger : logging.Logger
    _queue : list[MediaSource]
    current_source : tuple[MediaSource, discord.PCMVolumeTransformer]
    _terminating : bool
    _locked : bool
    repeat : bool
    _ignore_repeat : bool

    def __init__(self, 
                invoker : discord.Member, 
                channel : discord.VoiceChannel,
                guild : discord.Guild,
                client : Core.PYMusicBot.PYMusicBot) -> None:
        self.invoker = invoker
        self.channel = channel
        self.guild = guild
        self._client = client
        self._voice_client = None
        self.logger = logging.getLogger(f"PlayerInstance-{guild.id}")
        self._queue = []
        self.current_source = None
        self._terminating = False
        self._locked = False
        self.repeat = False
        self._ignore_repeat = False
        client.event(self.on_voice_state_update)

    async def on_voice_state_update(self, member : discord.Member, 
                                    before : discord.VoiceState, 
                                    after : discord.VoiceState):
        if self._terminating: return

        if self.members_in_voice < 1:
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
        self.logger.info(f"Reading the first 20ms from the audio source to avoid a speed up...")
        audio_src = get_ffmpeg_audio_src(source.url)
        audio_src.read()

        audio_src_wrapper = discord.PCMVolumeTransformer(audio_src, 1)
        source.start_time = int(time())
        self.current_source = (source, audio_src_wrapper)

        self._voice_client.play(audio_src_wrapper, after=self._on_source_end__wrapper)
        self.logger.info(f"Now playing {source.source_url}")

    # QEBL = Queue Ended But Locked
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

        self.logger.info("Stopping all votes")
        await stop_all_votes()

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

    @property
    def members_in_voice(self) -> int:
        return len(self.channel.members) - 1