import discord
import Utils
from Commands.CommandHandler import CommandDeclaration, CommandHandler
from PYMusicBot import PYMusicBot

@CommandDeclaration("join", CommandHandler("Joins the defined voice channel",
                                           needs_join_voice_channel=False, 
                                           needs_listening_executor=False))
async def cmd_join(instance : PYMusicBot, 
             message : discord.message.Message, 
             channel : discord.channel.TextChannel, 
             guild : discord.guild.Guild,
             args : list[str]):
    if not message.author.voice:
        await message.reply(embed=Utils.get_error_embed("You are currently not in a voice channel!"))
        return
    author_voice_channel = message.author.voice.channel
    author_voice_channel_permissions = author_voice_channel.permissions_for(instance.guild_member)

    if Utils.is_something_banned(author_voice_channel.id, 
                                 instance.config.BANNED_VOICE_CHANNELS, 
                                 instance.config.BANNED_VOICE_CHANNELS_IS_WHITELIST):
        await message.reply(embed=Utils.get_error_embed("Sorry, but your voice channel has been blocked from being used!"))
        return

    if not author_voice_channel_permissions.connect or not author_voice_channel_permissions.speak:
        await message.reply(embed=Utils.get_error_embed("I don't have enough permissions to join that channel!"))
        return

    if instance.is_joining:
        await message.reply(embed=Utils.get_error_embed("I am already attempting to join a channel!"))
        return

    if instance.get_voice_client():
        await instance.leave_voice_channel()
        
    instance.voice_channel = author_voice_channel
    instance.logger.info(f"Joining voice channel {author_voice_channel.id}...")

    try:
        instance.is_joining = True
        instance._voice_client = await instance.voice_channel.connect(timeout=10, reconnect=False, self_deaf=True)
    except TimeoutError:
        instance.logger.error(f"Timed out whilst trying to join the voice channel {author_voice_channel.id}!")
        await message.reply(embed=Utils.get_error_embed("Timed out whilst trying to join! Try again?"))
        return
    finally:
        instance.is_joining = False

    instance.logger.info(f"Starting loop on_vc_check_tick (interval: {instance.config.VC_CHECK_TICK_INTERVAL})...")
    instance.on_vc_check_tick.change_interval(seconds=instance.config.VC_CHECK_TICK_INTERVAL)
    if not instance.on_vc_check_tick.is_running():
        instance.on_vc_check_tick.start()

    await Utils.add_reaction(message, "✅")