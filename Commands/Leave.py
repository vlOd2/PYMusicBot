import discord
from Commands.CommandHandler import CommandDeclaration, CommandHandler
from PYMusicBot import PYMusicBot

@CommandDeclaration("leave", CommandHandler("Leaves the voice channel"))
async def cmd_leave(instance : PYMusicBot, 
             message : discord.message.Message, 
             channel : discord.channel.TextChannel, 
             guild : discord.guild.Guild,
             args : list[str]):
    await instance.leave_voice_channel()
    await message.add_reaction("✅")