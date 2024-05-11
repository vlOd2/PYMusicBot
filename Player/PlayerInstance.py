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
        self._logger : logging.Logger = logging.getLogger(f"PlayerInstance-{guild.id}")
        self._queue : list[MediaSource] = []
        self.current_source : tuple[MediaSource, FFmpegAudioSource] = None
        self._terminating = False
        client.event(self.on_voice_state_update)

    async def on_voice_state_update(self, member : discord.Member, 
                                    before : discord.VoiceState, 
                                    after : discord.VoiceState):
        if member == self._client.user and after.channel == None and not self._terminating:
            self._logger.info("Voice state reports we have been disconnected, cleaning up...")
            await self.stop()

    async def start(self):
        self._logger.info(f"Connecting to {self.channel.name} ({self.channel.id})...")
        self._voice_client = await self.channel.connect(reconnect=True, self_deaf=True)

    async def stop(self, noremove = False):
        if self._terminating: return
        self._logger.info("Disconnecting...")
        self._terminating = True
        await self._voice_client.disconnect(force=True)
        if not noremove: self._client.players.remove(self)

    async def _play(self, source : MediaSource):
        self._logger.info(f"Now playing {source.source_url}")
        raw_source = FFmpegAudioSource.get_instance(source.url, 1)
        self.current_source = (source, raw_source)
        self._voice_client.play(raw_source, 
                                after=lambda e: asyncio.run_coroutine_threadsafe(self.on_source_end(), self._client.loop))

    async def on_source_end(self):
        if self._terminating: return
        self._logger.info("Playback of current source ended")

        if len(self._queue) == 0:
            self._logger.info("Queue is empty, disconnecting...")
            await self.stop()
            return
            
        await self._play(self._queue.pop(0))

    async def add_queue(self, source : MediaSource) -> bool:
        if len(self._queue) == 0 and not self.current_source:
            await self._play(source)
            return False
        else:
            self._queue.append(source)
            return True

    def clear_queue(self):
        self._queue.clear()