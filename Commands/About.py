import discord
from Commands.CommandHandler import CommandDeclaration, CommandHandler
from PYMusicBot import PYMusicBot, VERSION

ABOUT_DESCRIPTION = (
    "PYMusicBot - v%VERSION%\n\n" + 
    "A free open-source bot that plays music in your Discord server.\n" + 
    "It is designed to be robust and easy to setup.\n" + 
    "Learn how to setup your own [here](https://github.com/vlOd2/PYMusicBot)\n\n" + 
    "You can list all the available commands by using the command `help`"
)

@CommandDeclaration("about", CommandHandler("Gets information about the bot", 
                                            needs_join_voice_channel=False, 
                                            needs_listening_executor=False))
async def cmd_about(instance : PYMusicBot, 
             message : discord.message.Message, 
             channel : discord.channel.TextChannel, 
             guild : discord.guild.Guild,
             args : list[str]):
    embed = discord.Embed()
    embed.colour = discord.Colour.from_rgb(0, 255, 0)
    embed.title = "About PYMusicBot"
    embed.description = ABOUT_DESCRIPTION.replace("%VERSION%", VERSION)
    embed.set_footer(text="PYMusicBot")
    await message.reply(embed=embed)