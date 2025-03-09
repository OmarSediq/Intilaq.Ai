from fastapi import FastAPI, UploadFile, File
import whisper
import tempfile
import os
import torch

app = FastAPI()

model = whisper.load_model("small", download_root="/root/.cache/whisper", device="cpu")

for m in model.modules():
    if isinstance(m, torch.nn.Module):
        m.half = False  # تعطيل FP16
        m.to(torch.float32)  # فرض FP32

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False) as temp_audio:
            temp_audio.write(file.file.read())
            temp_audio_path = temp_audio.name

        result = model.transcribe(temp_audio_path)
        os.remove(temp_audio_path)

        return {"text": result["text"]}

    except Exception as e:
        return {"error": str(e)}

# async def transcribe_audio(file):
  
#     url = "http://whisper_service:5001/transcribe" 
#     files = {"file": file}

#     async with httpx.AsyncClient() as client:
#         response = await client.post(url, files=files)

#     return response.json()["text"]
