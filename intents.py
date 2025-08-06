import discord

def ApplicationIntents():
    intents = discord.Intents.default()
    intents.message_content = True
    intents.bans = False
    intents.presences = True
    intents.voice_states = True
    return intents