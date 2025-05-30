import os
import whisper
import torch
from threading import Lock

_model_instance = None
_model_Lock = Lock()

def get_whisper_model():
    global _model_instance

    if _model_instance is None:
        with _model_Lock:
            if _model_instance is None:


                model_path = os.getenv("WHISPER_MODEL_PATH", "/whisper_model")
                model_name = os.getenv("WHISPER_MODEL_NAME", "base.en")

                device = "cuda" if torch.cuda.is_available() else "cpu"


                _model_instance = whisper.load_model(
                    model_name,
                    download_root=model_path,
                    device=device
                )
    else:
        print("[Whisper Loader] Reusing existing Whisper model")

    return _model_instance
