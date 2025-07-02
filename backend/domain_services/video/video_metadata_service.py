import subprocess
import tempfile

class VideoMetadataService:
    def get_duration(self, video_bytes: bytes) -> float:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_video:
            temp_video.write(video_bytes)
            temp_video_path = temp_video.name

        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            temp_video_path
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True , timeout=1200)

        try:
            return float(result.stdout.strip())
        except Exception:
            return -1.0
