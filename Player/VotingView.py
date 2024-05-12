import discord
import EmbedUtils
from PYMusicBot import PYMusicBot
from Player.PlayerInstance import PlayerInstance
from Commands.Util.CommandUtils import channel_check
from typing import Callable

_VOTE_TIMEOUT = 15

class VotingView(discord.ui.View):
    InstanceDict : dict[str, discord.ui.View] = {}

    @staticmethod
    def id_to_msg(action_id : str) -> str:
        match action_id:
            case "skip":
                return "skip the current song"
            case "stop":
                return "stop the player"
            case _:
                return "(unknown action)"

    def __init__(self, action_id : str, required : int, invoker : discord.User, on_success : Callable):
        '''
        Valid action IDs:
        - skip
        - stop
        '''
        super().__init__(timeout=_VOTE_TIMEOUT)
        self._action_id : str = action_id
        self._required : int = required + 1
        self._done : bool = False
        self._invoker : discord.User = invoker
        self._votes : list[int] = [ invoker.id ]
        self._on_success : Callable = on_success
        self.msg : discord.Message

        if action_id in VotingView.InstanceDict.keys():
            older_view : VotingView = VotingView.InstanceDict[action_id]
            
            if not older_view._done:
                # Previous vote outgoing
                self._done = True
                self.stop()
            else:
                # Previous vote ended
                VotingView.InstanceDict.pop(action_id)
                VotingView.InstanceDict[action_id] = self
        else:
            VotingView.InstanceDict[action_id] = self

    async def on_timeout(self):
        self._done = True
        await self.msg.edit(embed=EmbedUtils.error(
            "Vote timed out",
            "This vote has timed out. You can't participate anymore!",
            self._invoker
        ), view=None)

    async def update(self):
        if self._done: 
            await self.msg.edit(content="Another vote of this type is already outgoing!", view=None)
            self.stop()
            return
        
        await self.msg.edit(content=None, embed=EmbedUtils.state(
            "Vote",
            f"{self._invoker.name} would like to {VotingView.id_to_msg(self._action_id)}\n" +
            f"**{len(self._votes)}** votes out of the needed **{self._required}**\n" +
            f"This vote will time out in {_VOTE_TIMEOUT} seconds if nobody votes",
            self._invoker
        ), view=self)

    @discord.ui.button(label="Vote", style=discord.ButtonStyle.success)
    async def btn_vote_yes(self, e : discord.Interaction, btn : discord.ui.Button):
        if self._done: return

        client : PYMusicBot = e.client
        player : PlayerInstance | None = client.get_player(e.guild)
        if not await channel_check(e, player): return

        if e.user.id in self._votes:
            await e.response.send_message(embed=EmbedUtils.error(
                "Already voted",
                "You can't vote twice",
                e.user
            ), ephemeral=True)
            return
        
        self._votes.append(e.user.id)
        await self.update()
        await e.response.edit_message(view=self)

        if len(self._votes) >= self._required:
            self._done = True
            await self.msg.edit(embed=EmbedUtils.success(
                "Successful vote",
                "This vote was successful and has ended. You can't participate anymore!",
                self._invoker
            ), view=None)
            await self._on_success()
            self.stop()