class CommandHandler():
    def __init__(self, 
                 description="No description specified", 
                 needs_join_voice_channel=True,
                 needs_listening_executor=True, 
                 needs_admin=False) -> None:
        self.func = None
        self.description = description
        self.needs_join_voice_channel = needs_join_voice_channel
        self.needs_listening_executor = needs_listening_executor
        self.needs_admin = needs_admin

REGISTERED_CMDS : dict[str, CommandHandler] = {}

def CommandDeclaration(cmd, handler):
    def wrapper(func):
        handler.func = func
        REGISTERED_CMDS[cmd] = handler
        return func
    return wrapper