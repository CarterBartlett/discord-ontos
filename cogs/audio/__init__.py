from discord.ext import commands
from discord import app_commands

class Audio(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.__class__.__name__} is ready!')

    @app_commands.command(name='summon', description='Summon the bot to your voice channel')
    async def summon(self, interaction):
        if interaction.user.voice:
            channel = interaction.user.voice.channel
            await channel.connect()
            await interaction.response.send_message(f'Summoned to {channel.name}!', ephemeral=True)
        else:
            await interaction.response.send_message('You are not connected to a voice channel!', ephemeral=True)

    @app_commands.command(name='dismiss', description='Make the bot leave the voice channel')
    async def dismiss(self, interaction):
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.disconnect()
            await interaction.response.send_message('Disconnected from the voice channel!', ephemeral=True)
        else:
            await interaction.response.send_message('I am not connected to a voice channel!', ephemeral=True)

    # TODO: Implement play functionality
    @app_commands.command(name='play', description='Play audio in the voice channel')
    async def play(self, interaction, url: str):
        return True  # Placeholder for play functionality
async def setup(bot):
    await bot.add_cog(Audio(bot=bot))