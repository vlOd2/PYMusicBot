# Command template
# Copy this to create a basic command

# import discord
# import EmbedUtils
# from .CommandUtils import definecmd, fetch_check, playing_check, channel_check
# from PYMusicBot import PYMusicBot
# from Player.PlayerInstance import PlayerInstance

# @definecmd("", 
#            "")
# async def cmd_<name>(e : discord.Interaction):
#     client : PYMusicBot = e.client
#     player : PlayerInstance | None = client.get_player(e.guild)

#     if not await playing_check(e, player) or not await channel_check(e, player) or not await fetch_check(e, player):
#         return

#     await e.response.send_message(embed=EmbedUtils.state(
#         "I'm alive!",
#         "The bot is working perfectly fine!",
#         e.user
#     ))