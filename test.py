import requests
import yt_dlp
import simpleaudio as sa

ffmpeg_opts = {}
opts = {
    'format': 'bestaudio/best',
    'outtmpl': '%(title)s.%(ext)s',
    'quiet': True,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

URL = 'https://www.youtube.com/watch?v=8yOskhDn468'

with yt_dlp.YoutubeDL(opts) as ydl:
    info = ydl.extract_info(URL, download=False)
    url2 = info['url']
    print(url2)