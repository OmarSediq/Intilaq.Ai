import os
import whisper
from threading import Lock

_model_instance = None
_model_lock = Lock()

def get_whisper_model():
    global _model_instance

    if _model_instance is None:
        with _model_lock:
           
            if _model_instance is None:
                model_path = os.getenv("WHISPER_MODEL_PATH", "/whisper_model")
                model_name = os.getenv("WHISPER_MODEL_NAME", "base.en")
                _model_instance = whisper.load_model(model_name, download_root=model_path, device="cpu")

    return _model_instance
