import discord
import Utils
import logging
from Commands.CommandHandler import CommandDeclaration, CommandHandler
from PYMusicBot import PYMusicBot

@CommandDeclaration("adminonlymode", CommandHandler("Toggles the administrator only mode", needs_admin=True))
async def cmd_adminonlymode(instance : PYMusicBot, 
             message : discord.message.Message, 
             channel : discord.channel.TextChannel, 
             guild : discord.guild.Guild,
             args : list[str]):
    instance.config.COMMANDS_ADMIN_ONLY = not instance.config.COMMANDS_ADMIN_ONLY
    instance.config.save()
    logging.getLogger().info(f"{message.author} toggled COMMANDS_ADMIN_ONLY to {instance.config.COMMANDS_ADMIN_ONLY}")
    await message.reply(embed=Utils.get_embed(":shield: Administrator Only Mode Status", 
                                                f"The administrator only mode status was set to: {instance.config.COMMANDS_ADMIN_ONLY}", 
                                                (0, 255, 0)))