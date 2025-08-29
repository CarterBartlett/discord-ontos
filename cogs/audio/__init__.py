from discord.ext import commands
from discord import app_commands, FFmpegOpusAudio
import yt_dlp
from collections import deque
import asyncio
from cogs.audio.utils.playlist import Playlist
import os
import base64

yt_dlp_opts = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'youtube_include_dash_manifest': False,
    'youtube_include_hls_manifest': False,
}

env_cookies = os.environ.get('YOUTUBE_COOKIES')
if env_cookies: 
    try:
        # Check if env_cookies is base64 encoded (contains only base64 chars and is decodable)
        base64_bytes = env_cookies.encode('utf-8')
        decoded_bytes = base64.b64decode(base64_bytes, validate=True)
        env_cookies = decoded_bytes.decode('utf-8')
    except Exception:
        pass

    cookies_path = os.path.abspath('cookies.txt')
    with open(cookies_path, 'w') as f:
        f.write(env_cookies)
        yt_dlp_opts['cookiefile'] = cookies_path
        print(f"Using provided YouTube cookies for yt-dlp. Cookies file located at: {cookies_path}")
else:
    if os.path.exists('cookies.txt'):
        os.remove('cookies.txt')
    print('No cookies specified for yt-dlp.')

ffmpeg_opts = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -c:a libopus -b:a 96k'
}

PLAYLISTS = {}
GUILD_SETTINGS = {}

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

    @app_commands.command(name='nowplaying', description='View the currently playing song')
    async def nowplaying(self, interaction):
        guild_id = str(interaction.guild.id)
        if guild_id in PLAYLISTS and PLAYLISTS[guild_id]:
            now_playing = PLAYLISTS[guild_id].get_current()
            await interaction.response.send_message(f'Now playing: {now_playing[1]}')
        else:
            await interaction.response.send_message('No song is currently playing.')

    @app_commands.command(name='queue', description='View the current song queue')
    async def queue(self, interaction):
        guild_id = str(interaction.guild.id)
        if guild_id in PLAYLISTS and PLAYLISTS[guild_id]:
            now_playing = PLAYLISTS[guild_id].get_current()
            queue_list = "\n".join([title for _, title in PLAYLISTS[guild_id].get_remaining()])
            await interaction.response.send_message(f'Now playing: {now_playing[1]}\n\nCurrent queue:\n{queue_list}')
        else:
            await interaction.response.send_message('The queue is currently empty.')

    @app_commands.command(name='dismiss', description='Make the bot leave the voice channel')
    async def dismiss(self, interaction):
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.disconnect()
            await interaction.response.send_message('Disconnected from the voice channel!', ephemeral=True)
        else:
            await interaction.response.send_message('I am not connected to a voice channel!', ephemeral=True)

    @app_commands.command(name='play', description='Play audio in the voice channel')
    @app_commands.describe(query='Search query or URL')
    async def play(self, interaction, query: str):
        await interaction.response.defer(ephemeral=True)    

        if not interaction.guild.voice_client:
            if not interaction.user.voice.channel:
                return await interaction.response.send_message('You are not connected to a voice channel!', ephemeral=True)
            channel = interaction.user.voice.channel
            await channel.connect()
        
        guild_id = str(interaction.guild.id)
        voice_client = interaction.guild.voice_client
        voice_channel = interaction.channel

        if guild_id not in PLAYLISTS:
            PLAYLISTS[guild_id] = Playlist()

        with yt_dlp.YoutubeDL(yt_dlp_opts) as ydl:
            if (query.startswith('http://') or query.startswith('https://')):
                info = ydl.extract_info(query, download=False)
            else:
                info = ydl.extract_info(f'ytsearch:{query}', download=False)
                info = info['entries'][0] if 'entries' in info else info

            url = info['url']
            title = info['title']
            PLAYLISTS[guild_id].add((url, title))


        if voice_client.is_playing():
            await interaction.followup.send(f'Added to queue: {title}')
        else:
            await interaction.followup.send(f'Now playing: {title}')
            await play_song(voice_client, guild_id, voice_channel)

        return True

    @app_commands.command(name='skip', description='Skip the current song')
    async def skip(self, interaction):
        if not interaction.guild.voice_client:
            await interaction.response.send_message('Nothing playing to skip!', ephemeral=True)
            return
        
        voice_client = interaction.guild.voice_client
        if voice_client.is_playing() or voice_client.is_paused():
            interaction.guild.voice_client.stop()
            await interaction.response.send_message('Skipped the current song.', ephemeral=True)
        
    @app_commands.command(name='pause', description='Pause the current song')
    async def pause(self, interaction):
        voice_client = interaction.guild.voice_client

        if not voice_client:
            return await interaction.response.send_message('I am not connected to a voice channel!', ephemeral=True)

        if not voice_client.is_playing():
            return await interaction.response.send_message('No audio is currently playing!', ephemeral=True)

        voice_client.pause()
        await interaction.response.send_message('Paused the current song.', ephemeral=True)

    @app_commands.command(name='stop', description='Stop the current song and clear the queue')
    async def stop(self, interaction):
        voice_client = interaction.guild.voice_client

        if not voice_client:
            return await interaction.response.send_message('I am not connected to a voice channel!', ephemeral=True)

        voice_client.stop()
        current_playlist = PLAYLISTS.get(str(interaction.guild.id))
        if current_playlist:
            current_playlist.clear()

        await interaction.response.send_message('Stopped the current song and cleared the queue.', ephemeral=True)

    @app_commands.command(name='resume', description='Resume the paused song')
    async def resume(self, interaction):
        voice_client = interaction.guild.voice_client

        if not voice_client:
            return await interaction.response.send_message('I am not connected to a voice channel!', ephemeral=True)

        if not voice_client.is_paused():
            return await interaction.response.send_message('No audio is currently paused!', ephemeral=True)

        voice_client.resume()
        await interaction.response.send_message('Resumed the current song.', ephemeral=True)
    
    @app_commands.command(name='clear', description='Clear the current song queue')
    async def clear(self, interaction):
        voice_client = interaction.guild.voice_client

        if not voice_client:
            return await interaction.response.send_message('I am not connected to a voice channel!', ephemeral=True)

        current_playlist = PLAYLISTS.get(str(interaction.guild.id))
        if not current_playlist:
            return await interaction.response.send_message('No songs in the queue to clear!', ephemeral=True)

        current_playlist.clear()
        await interaction.response.send_message('Cleared the current song queue.', ephemeral=True)

    @app_commands.command(name='loop', description='Toggle looping')
    async def loop(self, interaction):
        settings = GUILD_SETTINGS.get(str(interaction.guild.id), {})

        if 'loop' not in settings:
            settings['loop'] = True
        else:
            settings['loop'] = not settings['loop']

        GUILD_SETTINGS[str(interaction.guild.id)] = settings
        await interaction.response.send_message(f"Looping is now {'enabled' if settings['loop'] else 'disabled'}.", ephemeral=True)
    
async def play_song(voice_client, guild_id, channel):
    current_playlist = PLAYLISTS.get(guild_id)
    settings = GUILD_SETTINGS.get(str(guild_id), {})

    # Reset the playlist if looping is enabled
    if settings.get('loop', False) and current_playlist and current_playlist.at_end_of_playlist():
        current_playlist.reset_pointer()

    if not current_playlist or current_playlist.is_empty() or not current_playlist.has_remaining_or_current():
        await voice_client.disconnect()
        return

    song = current_playlist.step()

    if not song:
        await voice_client.disconnect()
        current_playlist.clear()
        return

    audio_url, title = song

    source = FFmpegOpusAudio(audio_url, **ffmpeg_opts, executable='cogs\\audio\\bin\\ffmpeg\\ffmpeg.exe')

    def after_play(e):
        if e:
            print(f'Error playing {title}: {e}')
        asyncio.run_coroutine_threadsafe(play_song(voice_client, guild_id, channel), voice_client.loop)

    voice_client.play(source, after=after_play)

    asyncio.create_task(channel.send(f'Now playing: {title}'))

async def setup(bot):
    await bot.add_cog(Audio(bot=bot))