import discord
import Constants

def success(title : str, 
            description : str, 
            user : discord.User | discord.Member) -> discord.Embed:
    return _get_embed(title, 
                      description, 
                      Constants.EMBED_COLOR_SUCCESS, 
                      user)

def error(title : str, 
          description : str, 
          user : discord.User | discord.Member) -> discord.Embed:
    return _get_embed(title, 
                      description, 
                      Constants.EMBED_COLOR_ERROR, 
                      user)

def state(title : str, 
          description : str, 
          user : discord.User | discord.Member) -> discord.Embed:
    return _get_embed(title, 
                      description, 
                      Constants.EMBED_COLOR_STATE,  
                      user)

def _get_embed(title : str, 
               description : str, 
               color : int, 
               user : discord.User | discord.Member):
    embed = discord.Embed(title=title, 
                          description=description, 
                          colour=color)
    add_fields(user, embed)
    return embed

def add_fields(user : discord.User | discord.Member, embed : discord.Embed):
    if user != None:
      embed.set_author(name=user.name, icon_url=user.display_avatar.url)
    embed.set_footer(text=f"{Constants.EMBED_FOOTER}")