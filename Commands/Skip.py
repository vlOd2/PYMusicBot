import discord
import Utils
from Commands.CommandHandler import CommandDeclaration, CommandHandler
from PYMusicBot import PYMusicBot

@CommandDeclaration("skip", CommandHandler("Skips the current song and streams the next item in queue"))
async def cmd_skip(instance : PYMusicBot, 
             message : discord.message.Message, 
             channel : discord.channel.TextChannel, 
             guild : discord.guild.Guild,
             args : list[str]):
    instance.get_voice_client().stop()
    await Utils.add_reaction(message, "✅")