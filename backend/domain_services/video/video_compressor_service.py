import os
import tempfile
import subprocess

from backend.core.base_service import TraceableService


class VideoCompressorService(TraceableService):
    def __init__(self, crf: int = 32, preset: str = "veryfast"):
        self.crf = crf
        self.preset = preset

    async def compress_video(self, video_bytes: bytes) -> bytes:
        input_path = None
        output_path = None

        try:
            if not video_bytes or len(video_bytes) < 100:
                raise ValueError("Video file is empty or too small to compress.")

            with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as input_video:
                input_video.write(video_bytes)
                input_path = input_video.name

            print(f"[DEBUG] Video saved at: {input_path}, size: {len(video_bytes)} bytes")

            output_path = f"{input_path}_compressed.webm"

            cmd = [
                "ffmpeg",
                "-i", input_path,
                "-vcodec", "libvpx-vp9",
                "-crf", str(self.crf),
                "-b:v", "0",
                "-preset", self.preset,
                output_path,
                "-y"
            ]

            try:
                result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            except subprocess.CalledProcessError as e:
                print("FFMPEG ERROR:", e.stderr.decode())
                raise

            with open(output_path, "rb") as output_file:
                compressed_bytes = output_file.read()

            return compressed_bytes

        finally:
            if input_path and os.path.exists(input_path):
                os.remove(input_path)
            if output_path and os.path.exists(output_path):
                os.remove(output_path)
