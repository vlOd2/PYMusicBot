import discord

class PageView(discord.ui.View):
    def __init__(self, pages : list[str], timeout : float):
        super().__init__(timeout=timeout)
        self.pages : list[str] = pages
        self.current_page : int = 0

    async def respond(self, e : discord.Interaction):
        await e.response.edit_message(content=self.pages[self.current_page], view=self)        

    @discord.ui.button(label="<", style=discord.ButtonStyle.success)
    async def btn_prev_page(self, e : discord.Interaction, btn : discord.ui.Button):
        self.current_page -= 1
        if self.current_page < 0: self.current_page = len(self.pages) - 1
        await self.respond(e)

    @discord.ui.button(label=">", style=discord.ButtonStyle.success)
    async def btn_next_page(self, e : discord.Interaction, btn : discord.ui.Button):
        self.current_page += 1
        if self.current_page >= len(self.pages): self.current_page = 0
        await self.respond(e)