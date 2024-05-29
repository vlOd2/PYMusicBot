# This has got to be the shitiest code in the whole bot
import discord
import typing
from Core import EmbedUtils
from Core.PYMusicBot import PYMusicBot
from Core.Config import _CONFIG, ConfigInstance as Config
from Core.Utils import friendly_str_to_bool
from discord import app_commands
from .Util.CommandUtils import definecmd, admin_check, guild_user_check

_CONFIG_TYPE_HINTS : dict[str, typing.Any] = typing.get_type_hints(_CONFIG)

@definecmd("editcfg", 
           "Edits/Views configuration options (admin-only)")
@app_commands.choices(entry_key=[
    app_commands.Choice(name="Presence text", value="PresenceText"),
    app_commands.Choice(name="Admin roles", value="AdminRoles"),
    app_commands.Choice(name="Admin users", value="AdminUsers"),
    app_commands.Choice(name="Banned channels", value="BannedChannels"),
    app_commands.Choice(name="Banned users", value="BannedUsers"),
    app_commands.Choice(name="URL host whitelist", value="URLHostWhitelist"),
    app_commands.Choice(name="Flip URL host whitelist", value="FlipURLHostWhitelist")
])
@app_commands.choices(action=[
    app_commands.Choice(name="View", value="view"),
    app_commands.Choice(name="Set (non-lists only)", value="set"),
    app_commands.Choice(name="Add (lists only)", value="add"),
    app_commands.Choice(name="Remove (lists only)", value="remove")
])
async def cmd_editcfg(e : discord.Interaction, entry_key : str, action : str, value : str = None):
    if not await guild_user_check(e) or not await admin_check(e): return
    client : PYMusicBot = e.client
    
    client.logger.info(f"EDITCFG: {e.user.id}/{e.user.name} {entry_key} {action} {value}")
    entry = Config.__dict__[entry_key]

    if action == "view":
        await e.response.send_message(embed=EmbedUtils.state(
            entry_key, 
            "\n".join([f"- `{e}`" for e in entry]) if isinstance(entry, list) else str(entry), 
            e.user), ephemeral=True)
        return  
    elif value == None:
        await e.response.send_message(embed=EmbedUtils.error(
            "No value", 
            "You didn't provide a value",
            e.user), ephemeral=True)
        return

    # Handle modification
    if isinstance(entry, list):
        # List handling
        if action == "set":
            await e.response.send_message(embed=EmbedUtils.error(
                "Invalid action", 
                "The specified action cannot be used for this entry",
                e.user), ephemeral=True)
            return
        
        list_item_type : type = typing.get_args(_CONFIG_TYPE_HINTS[entry_key])[0]
        try:
            if list_item_type == bool:
                value = friendly_str_to_bool(value)
            else:
                value = list_item_type(value)
        except ValueError:
            await e.response.send_message(embed=EmbedUtils.error(
                "Invalid value", 
                "The specified value cannot be used",
                e.user), ephemeral=True)
            return

        if action == "add":
            entry.append(value)
            await e.response.send_message(embed=EmbedUtils.success(
                "Configuration modified",
                f"A value has been added to the list `{entry_key}`",
                e.user
            ))
        elif action == "remove":
            try:
                entry.remove(value)
            except ValueError:
                await e.response.send_message(embed=EmbedUtils.error(
                    "Not present", 
                    "The specified value is not present in the list",
                    e.user), ephemeral=True)
                return
            
            await e.response.send_message(embed=EmbedUtils.error(
                "Configuration modified",
                f"A value has been removed from the list `{entry_key}`",
                e.user
            ))

    else:
        if action == "add" or action == "remove":
            await e.response.send_message(embed=EmbedUtils.error(
                "Invalid action", 
                "The specified action cannot be used for this entry",
                e.user), ephemeral=True)
            return

        try:
            if type(entry) == bool:
                Config.__dict__[entry_key] = friendly_str_to_bool(value)
            else:
                Config.__dict__[entry_key] = type(entry)(value)
        except ValueError:
            await e.response.send_message(embed=EmbedUtils.error(
                "Invalid value", 
                "The specified value cannot be used",
                e.user), ephemeral=True)
            return
        
        await e.response.send_message(embed=EmbedUtils.success(
            "Configuration modified",
            f"The value of `{entry_key}` has been modified",
            e.user
        ))

    await client.reload_config()