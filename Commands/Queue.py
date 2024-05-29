import discord
import EmbedUtils
import Constants
import math
from .Util.CommandUtils import definecmd, guild_user_check, fetch_check, playing_check, channel_check
from PYMusicBot import PYMusicBot
from Player.PlayerInstance import PlayerInstance
from Player.MediaSource import MediaSource
from Utils import formated_time 

class _QueueView(discord.ui.View):
    pages : list[discord.Embed]
    current_page : int
    msg : discord.Message

    def __init__(self, pages : list[discord.Embed]):
        super().__init__(timeout=Constants.QUEUE_VIEW_TIMEOUT)
        if len(pages) == 0: raise ValueError("No pages were provided")
        self.pages = pages
        self.current_page = 0
        for embed in self.pages: embed.add_field(name="Page", value="N/A", inline=False)

    def _clean_up(self):
        self.pages = None
        self.current_page = 0
        self.msg = None

    def stop(self) -> None:
        super().stop()
        self._clean_up()

    async def on_timeout(self) -> None:
        await self.msg.edit(view=None)
        self._clean_up()

    async def update(self, e : discord.Interaction, init = False):
        embed : discord.Embed = self.pages[self.current_page]
        embed.set_field_at(len(embed.fields) - 1, 
                           name="Page", 
                           value=f"{self.current_page + 1}/{len(self.pages)}", 
                           inline=False)

        if init:
            await e.response.send_message(embed=embed, view=self, ephemeral=True, silent=True)
            self.msg = await e.original_response()
        else:
            await e.response.edit_message(embed=embed, view=self)        

    @discord.ui.button(label="<", style=discord.ButtonStyle.primary)
    async def _btn_prev_page(self, e : discord.Interaction, btn : discord.ui.Button):
        self.current_page -= 1
        if self.current_page < 0: self.current_page = len(self.pages) - 1
        await self.update(e)

    @discord.ui.button(label=">", style=discord.ButtonStyle.primary)
    async def _btn_next_page(self, e : discord.Interaction, btn : discord.ui.Button):
        self.current_page += 1
        if self.current_page >= len(self.pages): self.current_page = 0
        await self.update(e)

@definecmd("queue", 
           "Lists the player's queue")
async def cmd_queue(e : discord.Interaction):
    if not await guild_user_check(e): return
    client : PYMusicBot = e.client
    player : PlayerInstance | None = client.get_player(e.guild)

    if not await playing_check(e, player) or not await fetch_check(e, player):
        return

    pages : list[discord.Embed] = []
    entries : list[MediaSource] = player._queue
    entry_count = len(entries)
    page_count = int(math.ceil(entry_count / Constants.QUEUE_ENTRIES_PER_PAGE))

    if entry_count < 1:
        await e.response.send_message(embed=EmbedUtils.error(
            title="Empty queue",
            description="There is nothing in the queue right now",
            user=e.user
        ), ephemeral=True)
        return
    
    current_source : MediaSource = player.current_source[0]

    for page in range(page_count):
        embed = discord.Embed(title="Queue", description="")

        for entry_idx in range(Constants.QUEUE_ENTRIES_PER_PAGE):
            global_idx = page * Constants.QUEUE_ENTRIES_PER_PAGE + entry_idx
            if global_idx >= len(entries): break
            entry = entries[global_idx]
            embed.description += (
                f"{global_idx + 1}\\." + 
                f" [`{entry.title}`]({entry.source_url})" + 
                f" ({formated_time(entry.duration)})" +
                f" - {entry.invoker.mention}\n"
            )

        embed.add_field(name="Currently playing", 
                        value=f"[`{current_source.title}`]({current_source.source_url})", 
                        inline=False)
        EmbedUtils.add_fields(e.user, embed)
        pages.append(embed)

    view = _QueueView(pages)
    await view.update(e, True)

    if page_count < 2:
        embed : discord.Embed = view.msg.embeds[0]
        embed.remove_field(len(embed.fields) - 1)
        await view.msg.edit(embed=embed, view=None)
        view.stop()