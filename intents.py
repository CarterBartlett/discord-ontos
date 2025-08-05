import discord

class ApplicationIntents(discord.Intents):
    def __init__(self):
        super().__init__()
        self = discord.Intents.default()
        self.message_content = True
        self.bans = False