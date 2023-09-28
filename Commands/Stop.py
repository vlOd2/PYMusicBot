import discord
import Utils
from Commands.CommandHandler import CommandDeclaration, CommandHandler
from PYMusicBot import PYMusicBot

@CommandDeclaration("stop", CommandHandler("Stops the current song and clears the queue"))
async def cmd_stop(instance : PYMusicBot, 
             message : discord.message.Message, 
             channel : discord.channel.TextChannel, 
             guild : discord.guild.Guild,
             args : list[str]):
    if instance.repeat_last_song:
        instance.suppress_queue_stream_on_stop = True
    instance.clear_music_queue()
    instance.get_voice_client().stop()
    instance.logger.info("Stopped streaming and cleared the queue")
    await Utils.add_reaction(message, "✅")