# Command template
# Copy this to create a basic command

# import discord
# from Core import EmbedUtils
# from Core.PYMusicBot import PYMusicBot
# from .Util.CommandUtils import definecmd, guild_user_check, fetch_check, playing_check, channel_check
# from Player.PlayerInstance import PlayerInstance

# @definecmd("", 
#            "")
# async def cmd_<name>(e : discord.Interaction):
#     if not await guild_user_check(e): return
#     client : PYMusicBot = e.client
#     player : PlayerInstance | None = client.get_player(e.guild)

#     if not await playing_check(e, player) or not await channel_check(e, player) or not await fetch_check(e, player):
#         return

#     await e.response.send_message(embed=EmbedUtils.state(
#         "I'm alive!",
#         "The bot is working perfectly fine!",
#         e.user
#     ))