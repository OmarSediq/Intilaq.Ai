from datetime import datetime, timezone
from fastapi import HTTPException
from backend.utils.response_schemas import error_response , success_response
from backend.data_access.postgres.cv.resume_repository import ResumeRepository
from backend.data_access.postgres.cv.header_repository import CVHeaderRepository
from backend.core.contracts.publishers.document_event_publisher import DocumentEventPublisher
from backend.core.contracts.events.event_envelope import EventEnvelope
from backend.data_access.mongo.home.cv_snapshot_repository import CVSnapshotRepository
from backend.utils.generate_ulid_utils import generate_ulid
from backend.domain_services.cv_services.cv_snapshot_builder_service import CVSnapshotBuilder
from backend.data_access.mongo.home.user_cv_state_repository import UserCVStateRepository
class CVResumeExportService:
    def __init__(
        self,
        resume_repo: ResumeRepository,
        snapshot_repo: CVSnapshotRepository,
        snapshot_builder: CVSnapshotBuilder,
        document_event_publisher: DocumentEventPublisher,
        header_repo: CVHeaderRepository,
        user_cv_state_repo: UserCVStateRepository

    ):
        
        self.resume_repo = resume_repo
        self.snapshot_repo = snapshot_repo
        self.snapshot_builder = snapshot_builder
        self.document_event_publisher = document_event_publisher
        self.header_repo = header_repo
        self.user_cv_state_repo = user_cv_state_repo


    async def execute(self, user_id:int ):
     
            # 1) Validation & fetch user data 
            header_id = await self.header_repo.get_header_id_by_user_id(user_id)
            if not header_id:
                raise HTTPException(status_code=404 , detail=" No header associated with this user")
            
            user_data = await self.resume_repo.get_user_by_header_id(header_id)
            if not user_data or int (user_data["user_id"]!= int(user_id)):
                return error_response(code=403 , error_message="You do not have permission")
          
            snapshot_data = self.snapshot_builder.build(user_data)

            snapshot_id = generate_ulid()
            await self.snapshot_repo.create_snapshot(
                snapshot_id=snapshot_id,
                user_id=user_id,
                data=snapshot_data,
                version=1

            )
            await self.user_cv_state_repo.set_current_snapshot(user_id=user_id,snapshot_id=snapshot_id)

                    # REDIS_STREAM_DOCUMENT=intilaq:event:document 
                    # REDIS_STREAM_NOTIFICATION =intilaq:event:notification
                    # REDIS_CONSUMER_GROUP_NOTIFICATION = intilaq:notification:email
                    # REDIS_CONSUMER_GROUP_DOCUMENT=intilaq:document:cv

            event = EventEnvelope(
                event_name="document.cv_generation.requested",
                version=1,
                occurred_at=datetime.now(timezone.utc),
                idempotency_key=generate_ulid(),
                payload={
                    "snapshot_id": snapshot_id,
                    "document_type": "cv",
                    "formats": ["html", "pdf", "docx"],
                },
            )
            
            await self.document_event_publisher.publish(event)
            return success_response(
                code=200,
                data={
                    "message": "Document generation scheduled.",
                    "snapshot_id": snapshot_id,
                },
            )
    
            



# async def download_from_gridfs(self, file_id: str, user_id: int):
#         try:
#             file_doc = await self.storage.get_file_metadata(file_id)
#             if not file_doc:
#                 return error_response(code=404, error_message="File not found")

#             user_id_from_file = str(file_doc.get("metadata", {}).get("user_id"))
#             if user_id_from_file != str(user_id):
#                 return error_response(code=403, error_message="You do not have access to this file")

#             content = await self.storage.download_pdf(file_id)

#             return StreamingResponse(
#                 io.BytesIO(content),
#                 media_type="application/pdf",
#                 headers={"Content-Disposition": f"attachment; filename={file_doc.get('filename', 'cv')}.pdf"}
#             )

#         except Exception as e:
#             return error_response(code=500, error_message=f"Error fetching resume: {str(e)}")
