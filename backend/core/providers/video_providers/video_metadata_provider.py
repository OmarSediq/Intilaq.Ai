from backend.domain_services.video.video_metadata_service import VideoMetadataService

def get_video_metadata_service() -> VideoMetadataService:
    return VideoMetadataService()
