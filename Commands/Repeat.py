import discord
import Utils
from Commands.CommandHandler import CommandDeclaration, CommandHandler
from PYMusicBot import PYMusicBot

@CommandDeclaration("repeat", CommandHandler("Toggles repeating the currently playing song"))
async def cmd_repeat(instance : PYMusicBot, 
             message : discord.message.Message, 
             channel : discord.channel.TextChannel, 
             guild : discord.guild.Guild,
             args : list[str]):
    instance.repeat_last_song = not instance.repeat_last_song
    await message.reply(embed=Utils.get_embed(":repeat: Repeating Status", 
                                                f"The repeating status was set to: {instance.repeat_last_song}", 
                                                (0, 255, 0)))