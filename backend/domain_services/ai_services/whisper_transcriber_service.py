import httpx
import tempfile
import os
import asyncio
import subprocess
from fastapi import UploadFile

WHISPER_URL = os.getenv("WHISPER_SERVICE_URL", "http://speech_to_text_service:5001/transcribe")

class WhisperTranscriberService:
    async def compress_to_webm(self, input_path: str) -> str:
        output_path = input_path.replace(".wav", ".webm")
        command = [
            "ffmpeg", "-i", input_path,
            "-c:a", "libopus", "-b:a", "32k",
            "-vn", output_path
        ]
        await asyncio.to_thread(subprocess.run, command, check=True)
        return output_path

    async def transcribe_audio(self, file: UploadFile) -> str:
        try:
            ext = os.path.splitext(file.filename)[-1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_audio:
                await asyncio.to_thread(file.file.seek, 0)
                await asyncio.to_thread(temp_audio.write, file.file.read())
                input_path = temp_audio.name

            # 2. اضغط الملف إلى .webm
            output_path = await self.compress_to_webm(input_path)

            # 3. اقرأ الملف المضغوط
            audio_bytes = await asyncio.to_thread(lambda: open(output_path, "rb").read())

            headers = {"Content-Type": "audio/webm"}
            async with httpx.AsyncClient() as client:
                response = await client.post(WHISPER_URL, content=audio_bytes, headers=headers)

            await asyncio.to_thread(os.remove, input_path)
            await asyncio.to_thread(os.remove, output_path)

            if response.status_code == 200:
                result = response.json()
                return result.get("text", "")
            else:
                return f"Whisper error {response.status_code}: {response.text}"

        except Exception as e:
            return f"Transcription failed: {str(e)}"
