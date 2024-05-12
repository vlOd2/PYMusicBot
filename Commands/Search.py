import discord
import asyncio
import Utils
import YoutubeDL
from Commands.CommandHandler import CommandDeclaration, CommandHandler
from PYMusicBot import PYMusicBot
from .Stream import cmd_stream

@CommandDeclaration("search", CommandHandler("Searches a query and provides the results"))
async def cmd_search(instance : PYMusicBot, 
             message : discord.message.Message, 
             channel : discord.channel.TextChannel, 
             guild : discord.guild.Guild,
             args : list[str]):
    if len(args) < 1:
        await message.reply(embed=Utils.get_error_embed("No query specified!"))
        return

    if instance.is_resolving:
        await message.reply(embed=Utils.get_error_embed("Cannot resolve for another query when already resolving"))
        return

    query = " ".join(args)
    instance.logger.info(f"Getting raw data for query \"{query}\"...")
    search_msg = await message.reply(embed=Utils.get_embed(":hourglass: Resolving Query", 
                                                           f"Resolving the query `{query}`, please wait, this might take a while...", 
                                                           (0, 0, 255)))

    try:
        instance.is_resolving = True
        search_data = await YoutubeDL.get_flat_query_raw_data(f"ytsearch10:{query}")
        search_entries = search_data["entries"]
    except Exception as ex:
        await message.reply(embed=Utils.get_error_embed(f"An error has occured: {ex}"))
        return
    finally:
        instance.is_resolving = False

    if not "entries" in search_data or len(search_entries) < 1:
        await message.reply(embed=Utils.get_error_embed("No results were found"))
        return
    
    search_msg_content = ""
    for index, entry in enumerate(search_entries):
        search_msg_content += f"{index}\. [`{entry['title']}`](<{entry['url']}>)\n"

    await search_msg.edit(embed=Utils.get_embed(":mag: Search entries", search_msg_content, (0, 255, 0)))
    search_msg_reactions = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
    valid_msg_reactions = []
    received_valid_reaction_event = asyncio.Event()

    for i in range(len(search_entries)):
        await search_msg.add_reaction(search_msg_reactions[i])
        valid_msg_reactions.append(search_msg_reactions[i])

    async def add_reaction(reaction : discord.Reaction, user : discord.User):
        if user.id != message.author.id:
            return
        
        if not str(reaction.emoji) in valid_msg_reactions:
            return

        received_valid_reaction_event.set()

        match str(reaction.emoji):
            case "0️⃣":
                await cmd_stream(instance, message, channel, guild, [search_entries[0]["url"]])
            case "1️⃣":
                await cmd_stream(instance, message, channel, guild, [search_entries[1]["url"]])
            case "2️⃣":
                await cmd_stream(instance, message, channel, guild, [search_entries[2]["url"]])
            case "3️⃣":
                await cmd_stream(instance, message, channel, guild, [search_entries[3]["url"]])
            case "4️⃣":
                await cmd_stream(instance, message, channel, guild, [search_entries[4]["url"]])
            case "5️⃣":
                await cmd_stream(instance, message, channel, guild, [search_entries[5]["url"]])
            case "6️⃣":
                await cmd_stream(instance, message, channel, guild, [search_entries[6]["url"]])
            case "7️⃣":
                await cmd_stream(instance, message, channel, guild, [search_entries[7]["url"]])
            case "8️⃣":
                await cmd_stream(instance, message, channel, guild, [search_entries[8]["url"]])
            case "9️⃣":
                await cmd_stream(instance, message, channel, guild, [search_entries[9]["url"]])

    while not received_valid_reaction_event.is_set():
        instance.logger.info("Search command -> waiting for valid reaction")
        await instance.wait_for("reaction_add", check=lambda reaction, user: 
                                asyncio.run_coroutine_threadsafe(add_reaction(reaction, user), instance.loop))
        try:
            await asyncio.wait_for(received_valid_reaction_event.wait(), 1)
            instance.logger.info("Search command -> received valid reaction")
            break
        except TimeoutError:
            instance.logger.info("Search command -> timed out whilst waiting for valid reaction, retrying...")