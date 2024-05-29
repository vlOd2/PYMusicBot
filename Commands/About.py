import discord
from Core import Constants
from Core.PYMusicBot import PYMusicBot
from Core.Utils import formated_time
from .Util.CommandUtils import definecmd, guild_user_check
from time import time

@definecmd("about", 
           "Gets information about the bot")
async def cmd_about(e : discord.Interaction):
    if not await guild_user_check(e): return
    client : PYMusicBot = e.client

    embed = discord.Embed(
        title="PYMusicBot V2", 
        url="https://github.com/vlOd2/PYMusicBot",
        colour=0xA020F0,
        description=(
            "A music bot designed to play various formats, be robust and easy to use\n" + 
            f"Made with :heart: by [vlOd](<https://github.com/vlOd2>)")
    )
    embed.add_field(name="Version", value=Constants.APP_VERSION)
    embed.add_field(name="Uptime", value=formated_time(int(time()) - client.start_time))

    await e.response.send_message(embed=embed, ephemeral=True)