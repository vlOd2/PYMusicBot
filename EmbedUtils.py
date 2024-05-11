import discord
import Constants

def success(title : str, 
          description : str, 
          client : discord.Client, 
          user : discord.User | discord.Member) -> discord.Embed:
    return _get_embed(title, 
                      description, 
                      Constants.EMBED_COLOR_SUCCESS, 
                      client, 
                      user)

def error(title : str, 
          description : str, 
          client : discord.Client, 
          user : discord.User | discord.Member) -> discord.Embed:
    return _get_embed(title, 
                      description, 
                      Constants.EMBED_COLOR_ERROR, 
                      client, 
                      user)

def state(title : str, 
          description : str, 
          client : discord.Client, 
          user : discord.User | discord.Member) -> discord.Embed:
    return _get_embed(title, 
                      description, 
                      Constants.EMBED_COLOR_STATE, 
                      client, 
                      user)

def _get_embed(title : str, 
               description : str, 
               color : int,
               client : discord.Client, 
               user : discord.User | discord.Member):
    embed = discord.Embed(title=title, 
                          description=description, 
                          colour=color)
    add_fields(client, user, embed)
    return embed

def add_fields(client : discord.Client, 
                     user : discord.User | discord.Member, 
                     embed : discord.Embed):
    embed.set_author(name=user.name, icon_url=user.display_avatar.url)
    embed.set_footer(text=f"{Constants.EMBED_FOOTER}")