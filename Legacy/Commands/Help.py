import discord
import Utils
from Commands.CommandHandler import CommandDeclaration, CommandHandler, REGISTERED_CMDS
from PYMusicBot import PYMusicBot

@CommandDeclaration("help", CommandHandler("Provides a list of available commands",
                                           needs_join_voice_channel=False, 
                                           needs_listening_executor=False))
async def cmd_help(instance : PYMusicBot, 
             message : discord.message.Message, 
             channel : discord.channel.TextChannel, 
             guild : discord.guild.Guild,
             args : list[str]):
    help_message = "** Users **\n"
    for cmd, cmd_handler in REGISTERED_CMDS.items():
        if cmd_handler.needs_admin: continue
        help_message += f"{cmd} - {cmd_handler.description}\n"
        
    help_message += "\n** Administrators **\n"
    for cmd, cmd_handler in REGISTERED_CMDS.items():
        if not cmd_handler.needs_admin: continue
        help_message += f"{cmd} - {cmd_handler.description}\n"

    await message.reply(embed=Utils.get_embed(
        ":information_source: Available Commands", 
        help_message, 
        (0, 255, 0)))