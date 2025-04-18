from fastapi import FastAPI, UploadFile, File
import whisper
import tempfile
import os
import torch
import shutil
import io
import warnings


warnings.filterwarnings("ignore", message="FP16 is not supported on CPU")

app = FastAPI()

model = whisper.load_model("base", download_root="/root/.cache/whisper", device="cpu")

for m in model.modules():
    if isinstance(m, torch.nn.Module):
        m.half = False 
        m.to(torch.float32) 


@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
            shutil.copyfileobj(file.file, temp_audio) 

            temp_audio_path = temp_audio.name
        result = model.transcribe(temp_audio_path)

        os.remove(temp_audio_path)

        return {"text": result["text"]}

    except Exception as e:
        return {"error": str(e)}


