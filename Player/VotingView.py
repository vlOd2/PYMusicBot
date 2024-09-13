import discord
from Core import EmbedUtils
from Core import Constants
from Core.PYMusicBot import PYMusicBot
from Core.Utils import utcnow_with_delta
from Player.PlayerInstance import PlayerInstance
from Commands.Util.CommandUtils import channel_check
from typing import Callable
from datetime import timedelta

class VotingView(discord.ui.View):
    InstanceDict : dict[str, discord.ui.View] = {}
    _action_id : str
    _required : int
    _done : bool
    _invoker : discord.User
    _votes : list[int]
    _on_success : Callable
    msg : discord.Message

    def __init__(self, action_id : str, required : int, invoker : discord.User, on_success : Callable):
        '''
        Valid action IDs:
        - skip
        - stop
        '''
        super().__init__(timeout=Constants.VOTE_TIMEOUT)
        self._action_id = action_id
        self._required = required + 1
        self._done = False
        self._invoker = invoker
        self._votes = [ invoker.id ]
        self._on_success = on_success
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

    @staticmethod
    def _id_to_msg(action_id : str) -> str:
        match action_id:
            case "skip":
                return "skip the current song"
            case "stop":
                return "stop the player"
            case _:
                return "(unknown action)"

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

        timeout_timestamp = round(utcnow_with_delta(timedelta(seconds=Constants.VOTE_TIMEOUT)).timestamp())
        await self.msg.edit(content=None, embed=EmbedUtils.state(
            "Vote",
            f"{self._invoker.name} would like to {VotingView._id_to_msg(self._action_id)}\n" +
            f"**{len(self._votes)}** votes out of the needed **{self._required}**\n" +
            f"This vote will time out in <t:{timeout_timestamp}:R> seconds if nobody votes",
            self._invoker
        ), view=self)

    async def mark_as_timedout(self):
        await self.on_timeout()
        self.stop()

    async def mark_as_done(self):
        self._done = True
        await self.msg.edit(embed=EmbedUtils.success(
            "Successful vote",
            "This vote was successful and has ended. You can't participate anymore!",
            self._invoker
        ), view=None)
        await self._on_success()
        self.stop()

    @discord.ui.button(label="Vote", style=discord.ButtonStyle.success)
    async def _btn_vote_yes(self, e : discord.Interaction, btn : discord.ui.Button):
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
            await self.mark_as_done()