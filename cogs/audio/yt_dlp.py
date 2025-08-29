import yt_dlp
import base64
import os

class ExtendedYoutubeDL(yt_dlp.YoutubeDL):
    def __init__(self, opts=None):
        if opts is None:
            opts = {}
        default_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'youtube_include_dash_manifest': False,
            'youtube_include_hls_manifest': False,
            'skip_download': True
        }
        self.opts = {**default_opts, **opts}
        super().__init__(self.opts)

    def extract_info_one(self, url, **kwargs):
        passed_opts = kwargs.get('opts', {})
        opts = {**self.opts, **passed_opts}
        with yt_dlp.YoutubeDL(opts) as ydl:
            if opts.cookie:
                ydl.cookiejar.set_cookie(opts.cookie)
            if url.startswith('http://') or url.startswith('https://'):
                return ydl.extract_info(url, **kwargs)
            else:
                info = ydl.extract_info(f'ytsearch:{url}', **kwargs)
                if info and 'entries' in info:
                    return info['entries'][0]
                return info

    def set_cookie(self, cookie):
        try:
            # Check if cookie is base64 encoded (contains only base64 chars and is decodable)
            base64_bytes = cookie.encode('utf-8')
            decoded_bytes = base64.b64decode(base64_bytes, validate=True)
            cookie = decoded_bytes.decode('utf-8')
        except Exception:
            pass

        cookies_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cookies.txt')
        with open(cookies_path, 'w') as f:
            f.write(cookie)
        self.opts['cookiefile'] = cookies_path
        print(f"Using provided YouTube cookies for yt-dlp. Cookies file located at: {cookies_path}")