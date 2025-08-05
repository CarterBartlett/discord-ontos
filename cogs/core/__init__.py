from discord.ext import commands
from discord import app_commands

class Core(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='invite', description='Get the bot invite link.')
    async def invite(self, interaction):
        invite_link = f'https://discord.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions={self.bot.intents.value}&scope=bot'
        await interaction.response.send_message(f'Invite link: {invite_link}')

    @app_commands.command(name='ping', description='Pong!')
    async def ping(self, interaction):
        await interaction.response.send_message('Pong!')

async def setup(bot):
    await bot.add_cog(Core(bot=bot))