import httpx
from fastapi import UploadFile
import tempfile  
import shutil    
import os 
import io
import mimetypes


WHISPER_URL = "http://whisper_service:5001/transcribe"

async def transcribe_audio(file: UploadFile):
    try:
        ext = os.path.splitext(file.filename)[-1]  
        mime_type, _ = mimetypes.guess_type(file.filename)

        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_audio:
            shutil.copyfileobj(file.file, temp_audio)
            temp_audio_path = temp_audio.name

        files = {
            "file": (file.filename, open(temp_audio_path, "rb"), mime_type or "application/octet-stream")
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(WHISPER_URL, files=files)

        os.remove(temp_audio_path)

        return response.json().get("text", "")

    except Exception as e:
        return {"error": str(e)}

