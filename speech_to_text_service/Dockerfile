# ========== Stage 1: Build & Download Whisper Model ==========
FROM python:3.10-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg libsndfile1 git libffi-dev && apt-get clean

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install debugpy

RUN python -c "import whisper; whisper.load_model('base.en', download_root='/whisper_model')"

# ========== Stage 2: Final Image ==========
FROM python:3.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg libsndfile1 && apt-get clean

WORKDIR /app
ENV PYTHONPATH=/app

COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /whisper_model /whisper_model

COPY . /app/speech_to_text_service

EXPOSE 5001
EXPOSE 5679


CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5679", "-m", "uvicorn", "speech_to_text_service.app.main:app", "--host", "0.0.0.0", "--port", "5001"]
