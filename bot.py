# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from discord.ext.commands import Bot
import json
from intents import ApplicationIntents
import os

BOT_TOKEN = os.getenv('DISCORD_API_TOKEN', None)
if not BOT_TOKEN:
    raise ValueError("DISCORD_API_TOKEN not found in environment variables.")

bot = Bot('!', intents=ApplicationIntents())

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')
    print(f'Intents value - {bot.intents.value}')
    print(f'Invite link: https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions={bot.intents.value}&scope=bot')

    with open('settings.json', 'r') as f:
        settings = json.load(f)

    loaded_cogs = []

    for cog in settings.get('loaded_cogs', []):
        try:
            cog_path = f'cogs.{cog}'
            await bot.load_extension(cog_path)
            loaded_cogs.append(cog)
        except Exception as e:
            print(f'Failed to load cog {cog}: {e}')
    
    print(f'Loaded cogs: {", ".join(loaded_cogs)}')
    await sync_commands()


async def sync_commands():
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} commands.')
    except Exception as e:
        print(f'Failed to sync commands: {e}')

bot.run(BOT_TOKEN)