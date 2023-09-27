import discord
import Utils
from Commands.CommandHandler import CommandDeclaration, CommandHandler
from PYMusicBot import PYMusicBot

@CommandDeclaration("forcestop", CommandHandler("Clears the queue and kills all voice clients", 
                                                needs_join_voice_channel=False, 
                                                needs_admin=True))
async def cmd_forcestop(instance : PYMusicBot, 
             message : discord.message.Message, 
             channel : discord.channel.TextChannel, 
             guild : discord.guild.Guild,
             args : list[str]):
    await instance.leave_voice_channel()
    for voice_client in instance.voice_clients:
        await voice_client.disconnect()
        voice_client.cleanup()
    await Utils.add_reaction(message, "✅")