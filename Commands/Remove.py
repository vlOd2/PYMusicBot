import discord
import Utils
from Commands.CommandHandler import CommandDeclaration, CommandHandler
from PYMusicBot import PYMusicBot

@CommandDeclaration("remove", CommandHandler("Removes a song from the queue"))
async def cmd_remove(instance : PYMusicBot, 
             message : discord.message.Message, 
             channel : discord.channel.TextChannel, 
             guild : discord.guild.Guild,
             args : list[str]):
    if len(args) < 1 or not args[0].isdigit():
        await message.reply(embed=Utils.get_embed(":information_source: Usage", "remove <number>", (0, 255, 0)))
        return

    song_number = int(args[0])
    if song_number < 0 or song_number > (len(instance.music_queue) - 1):
        await message.reply(embed=Utils.get_error_embed(f"Song with the number {song_number} is not in the queue range"))
        return
    
    del instance.music_queue[song_number]
    await message.add_reaction("✅")