
from backend.domain_services.video.video_compressor_service import VideoCompressorService
from backend.domain_services.video.audio_extractor_service import AudioExtractorService



def get_audio_extractor_service() -> AudioExtractorService:
    return AudioExtractorService(codec="libopus", bitrate="32k")

def get_video_compressor_service() -> VideoCompressorService:
    return VideoCompressorService(crf=32, preset="veryfast")

