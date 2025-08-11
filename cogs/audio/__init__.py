from discord.ext import commands
from discord import app_commands, FFmpegOpusAudio, PCMVolumeTransformer
import yt_dlp
from collections import deque
import asyncio
from cogs.audio.utils.playlist import Playlist

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
        
        voice_client = None
        guild_id = str(interaction.guild.id)

        # Join voice channel if not already connected and get voice client
        if not interaction.guild.voice_client:
            if not interaction.user.voice.channel:
                return await interaction.response.send_message('You are not connected to a voice channel!', ephemeral=True)
            voice_client = await join_voice_channel(interaction, interaction.user.voice.channel)
        else:
            voice_client = interaction.guild.voice_client
            
        # Create or get the playlist for the guild
        if guild_id not in PLAYLISTS:
            PLAYLISTS[guild_id] = Playlist()

        # Add the song to the playlist
        with yt_dlp.YoutubeDL(yt_dlp_opts) as ydl:
            if (query.startswith('http://') or query.startswith('https://')): # Direct URL
                info = ydl.extract_info(query, download=False)
            else: # Search query
                info = ydl.extract_info(f'ytsearch:{query}', download=False)
                info = info['entries'][0] if 'entries' in info else info

            PLAYLISTS[guild_id].add({'id': info['id'], 'url': info['url'], 'title': info['title'], 'duration': info['duration']})


        if voice_client.is_playing():
            await interaction.followup.send(f'Added to queue: {info["title"]}')
        else:
            await interaction.followup.send(f'Now playing: {info["title"]}')
            await play_song(voice_client, guild_id, voice_client.channel)

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
    
    # TODO: Test this command
    @app_commands.command(name='volume', description='Set the volume of the bot')
    async def volume(self, interaction, level: int):
        voice_client = interaction.guild.voice_client

        if not voice_client:
            return await interaction.response.send_message('I am not connected to a voice channel!', ephemeral=True)

        if level < 0 or level > 100:
            return await interaction.response.send_message('Volume level must be between 0 and 100.', ephemeral=True)

        voice_client.source = PCMVolumeTransformer(voice_client.source, volume=level / 100)
        await interaction.response.send_message(f"Volume set to {level}%.", ephemeral=True)

async def join_voice_channel(interaction, channel, **kwargs):
    silent = kwargs.get('silent', False)

    try:
        voice_client = await channel.connect()
        return voice_client
    except Exception as e:
        if not silent:
            await interaction.response.send_message(f"Error connecting to voice channel: {e}", ephemeral=True)
        return None

async def play_song(voice_client, guild_id, channel):
    current_playlist = PLAYLISTS.get(guild_id)
    settings = GUILD_SETTINGS.get(str(guild_id), {})

    # Reset the playlist if looping is enabled
    if settings.get('loop', False) and current_playlist and current_playlist.at_end_of_playlist():
        current_playlist.reset_pointer()

    if not current_playlist or current_playlist.is_empty() or not current_playlist.has_remaining_or_current():
        await voice_client.disconnect()
        return

    # Step through the playlist to get the next song    
    song = current_playlist.step()

    if not song:
        await voice_client.disconnect()
        current_playlist.clear()
        return

    title = song.get('title', 'Unknown Title')
    audio_url = song.get('url', None)

    source = FFmpegOpusAudio(audio_url, **ffmpeg_opts, executable='cogs\\audio\\bin\\ffmpeg\\ffmpeg.exe')

    def after_play(e):
        if e:
            print(f'Error playing {title}: {e}')
        asyncio.run_coroutine_threadsafe(play_song(voice_client, guild_id, channel), voice_client.loop)

    voice_client.play(source, after=after_play)

    asyncio.create_task(channel.send(f'Now playing: {title}'))

async def setup(bot):
    await bot.add_cog(Audio(bot=bot))