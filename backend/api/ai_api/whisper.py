# from fastapi import APIRouter, UploadFile, File, Depends
# from app.domain_services.ai_services.whisper_transcriber_service import WhisperTranscriberService
# from app.core.providers.domain_providers.ai_providers import get_whisper_transcriber_service
# from app.utils.response_schemas import success_response, error_response

# router = APIRouter(prefix="/api/ai/whisper", tags=["Whisper"])

# @router.post("/transcribe")
# async def transcribe_audio_route(
#     file: UploadFile = File(...),
#     whisper_service: WhisperTranscriberService = Depends(get_whisper_transcriber_service)
# ):
#     result = await whisper_service.transcribe_audio(file)
    
#     if isinstance(result, str) and result.startswith("Error"):
#         return error_response(code=500, error_message=result)
    
#     return success_response(code=200, data={"text": result})
