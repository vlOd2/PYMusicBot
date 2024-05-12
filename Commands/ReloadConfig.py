import discord
import Utils
from Commands.CommandHandler import CommandDeclaration, CommandHandler
from PYMusicBot import PYMusicBot

@CommandDeclaration("reloadconfig", CommandHandler("Reloads the configuration", 
                                                needs_join_voice_channel=False, 
                                                needs_admin=True))
async def cmd_reloadconfig(instance : PYMusicBot, 
             message : discord.message.Message, 
             channel : discord.channel.TextChannel, 
             guild : discord.guild.Guild,
             args : list[str]):
    # Does basically the same thing as the forcestop command
    await instance.leave_voice_channel()
    for voice_client in instance.voice_clients:
        await voice_client.disconnect()
        voice_client.cleanup()
    await instance.load_config()
    await Utils.add_reaction(message, "✅")