from discord.ext import commands
from discord import app_commands, FFmpegOpusAudio
import yt_dlp

yt_dlp_opts = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'youtube_include_dash_manifest': False,
    'youtube_include_hls_manifest': False,
}

ffmpeg_opts = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -c:a libopus -b:a 96k'
}

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

    # TODO: Create queueing system
    @app_commands.command(name='play', description='Play audio in the voice channel')
    async def play(self, interaction, url: str):
        if not interaction.guild.voice_client:
            channel = interaction.user.voice.channel
            await channel.connect()
        
        voice_client = interaction.guild.voice_client

        with yt_dlp.YoutubeDL(yt_dlp_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_stream_url = info['url']
        
        source = FFmpegOpusAudio(audio_stream_url, **ffmpeg_opts, executable='cogs\\audio\\bin\\ffmpeg\\ffmpeg.exe')

        voice_client.play(source)
        return True

async def setup(bot):
    await bot.add_cog(Audio(bot=bot))