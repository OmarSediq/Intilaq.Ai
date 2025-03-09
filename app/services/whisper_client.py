import httpx
from fastapi import UploadFile, File

WHISPER_URL = "http://whisper-container:5001/transcribe"


async def transcribe_audio(file: UploadFile):
    try:
        files = {"file": (file.filename, file.file, file.content_type)}

        async with httpx.AsyncClient() as client:
            response = await client.post(WHISPER_URL, files=files)

        return response.json().get("text", "")

    except Exception as e:
        return {"error": str(e)}
