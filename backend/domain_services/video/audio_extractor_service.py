import os
import tempfile
import subprocess
from typing import Optional

from backend.core.base_service import TraceableService


class AudioExtractorService(TraceableService):
    def __init__(self, codec: str = "libopus", bitrate: str = "32k"):
        self.codec = codec
        self.bitrate = bitrate

    async def extract_audio(self, video_bytes: bytes) -> Optional[bytes]:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as video_file:
                video_file.write(video_bytes)
                video_file_path = video_file.name

            audio_file_path = f"{video_file_path}_audio.webm"


            cmd = [
                "ffmpeg",
                "-i", video_file_path,
                "-vn",
                "-c:a", self.codec,
                "-b:a", self.bitrate,
                audio_file_path,
                "-y"
            ]

            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True , timeout=1200)

            with open(audio_file_path, "rb") as audio_file:
                audio_bytes = audio_file.read()

            return audio_bytes

        finally:
            # Cleanup
            if os.path.exists(video_file_path):
                os.remove(video_file_path)
            if os.path.exists(audio_file_path):
                os.remove(audio_file_path)
