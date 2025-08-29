import os
import sys
import platform
import requests
import zipfile
import tarfile
import shutil

class FFmpeg:
    def __init__(self):
        ffmpeg_path = shutil.which('ffmpeg')
        if (ffmpeg_path is not None):
            self.executable = ffmpeg_path
        else:
            self.executable = self.__setup_ffmpeg()

        self.opts = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn -c:a libopus -b:a 96k'
        }

    def __setup_ffmpeg(self):
        url = self.__get_ffmpeg_download_url()
        zip_path = self.download_file(url, url.split('/')[-1])
        return self.extract_file(zip_path)

    def __get_ffmpeg_download_url(self):
        system = platform.system().lower()
        arch = platform.machine().lower()
        if system == 'windows':
            return 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip'
        elif system == 'darwin':
            return 'https://evermeet.cx/ffmpeg/ffmpeg.zip'
        elif system == 'linux':
            # Use johnvansickle.com static builds for Linux x64
            if 'x86_64' in arch:
                return 'https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz'
            elif 'arm' in arch or 'aarch64' in arch:
                return 'https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-arm64-static.tar.xz'
        return None

    def download_file(self, url, filename):
        temp_download_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ffmpeg_temp')
        os.makedirs(temp_download_dir, exist_ok=True)
        filepath = os.path.join(temp_download_dir, filename)
        print(f"Downloading {url} ...")
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(filepath, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"Downloaded to {filepath}")
        return filepath

    def extract_file(self, filename):
        output = {
            'ffmpeg': None
        }
        ffmpeg_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bin')
        os.makedirs(ffmpeg_dir, exist_ok=True)
        if filename.endswith('.zip'):
            with zipfile.ZipFile(filename, 'r') as zip_ref:
                ffmpeg_exe = next((name for name in zip_ref.namelist() if name.endswith('ffmpeg.exe')), None)
                if ffmpeg_exe:
                    with zip_ref.open(ffmpeg_exe) as source, open(os.path.join(ffmpeg_dir, os.path.basename(ffmpeg_exe)), 'wb') as target:
                        target.write(source.read())
                        output['ffmpeg'] = target.name
                else:
                    print("ffmpeg.exe not found in the archive.")
            print("Downloaded ffmpeg.exe")
        elif filename.endswith('.tar.xz'):
            with tarfile.open(filename, 'r:xz') as tar_ref:
                ffmpeg_bin = next((member for member in tar_ref.getmembers() if member.name.endswith('/ffmpeg') or member.name.endswith('ffmpeg')), None)
                if ffmpeg_bin:
                    bin_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bin')
                    os.makedirs(bin_dir, exist_ok=True)
                    target_path = os.path.join(bin_dir, os.path.basename(ffmpeg_bin.name))
                    with tar_ref.extractfile(ffmpeg_bin) as source, open(target_path, 'wb') as target:
                        target.write(source.read())
                    os.chmod(target_path, 0o755)
                    output['ffmpeg'] = target_path
                else:
                    print("ffmpeg binary not found in the archive.")
            print("Downloaded ffmpeg.bin")
        return output
    
    def __str__(self):
        return f"FFmpeg executable: {self.ffmpeg}; FFmpeg options: {self.ffmpeg_opts}"