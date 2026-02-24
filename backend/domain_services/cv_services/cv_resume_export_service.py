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
class CVResumeExportService:
    def __init__(
        self,
        resume_repo: ResumeRepository,
        snapshot_repo: CVSnapshotRepository,
        snapshot_builder: CVSnapshotBuilder,
        document_event_publisher: DocumentEventPublisher,
        header_repo: CVHeaderRepository,

    ):
        
        self.resume_repo = resume_repo
        self.snapshot_repo = snapshot_repo
        self.snapshot_builder = snapshot_builder
        self.document_event_publisher = document_event_publisher
        self.header_repo = header_repo


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
                data=snapshot_data,
                version=1

            )

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

            


# async def generate_html_image(self, user_id: int):
#         try:
#             # 1) Validation & fetch user data
#             header_id = await self.header_repo.get_header_id_by_user_id(user_id)
#             if not header_id:
#                 raise HTTPException(status_code=404, detail="No header associated with this user")

#             user_data = await self.resume_repo.get_user_by_header_id(header_id)
#             if not user_data or int(user_data["user_id"]) != int(user_id):
#                 return error_response(code=403, error_message="You do not have permission")

#             # 2) idempotency key (ULID) - you may compute deterministic key instead if desired
#             idempotency_key = ulid.new().str

#             # Optional: check existing job by idempotency (job_repo.get_by_idempotency)
#             existing = await self.job_repo.get_by_idempotency(idempotency_key)
#             if existing:
#                 # return existing job info
#                 return success_response(code=200, data={"job_id": str(existing.id), "status": existing.status})

#             # 3) create pending job + empty render_detail (ORM repo handles transactions)
#             job_id = str(uuid.uuid4())
#             await self.job_repo.create_pending_job_with_render_detail(job_id, idempotency_key, user_id, "render")

#             # 4) render HTML via template (domain responsibility)
#             html_content = self.html_renderer.render(user_data)
#             # sanitize if you have a sanitizer utility:
#             # html_content = sanitize_html(html_content)

#             # 5) upload HTML to GridFS
#             filename = f"resume_html_{user_id}_{uuid.uuid4().hex}.html"
#             metadata = {
#                 "user_id": user_id,
#                 "header_id": header_id,
#                 "template_id": user_data.get("template_id", "default"),
#                 "created_at": datetime.utcnow().isoformat()
#             }
#             try:
#                 html_gridfs_id = await self.storage.upload_html(filename, html_content, metadata=metadata, gzip_compress=True)
#             except Exception as e:
#                 # mark job failed if upload fails
#                 await self.job_repo.mark_job_failed(job_id, f"gridfs_upload_failed: {e}")
#                 return error_response(code=500, error_message=f"Failed to upload HTML: {str(e)}")

#             # 6) update render_detail and mark job queued
#             renderer_options = {"width": 1200, "scale": 2}
#             try:
#                 await self.job_repo.update_render_detail(job_id, html_gridfs_id, filename, renderer_options)
#                 await self.job_repo.mark_job_queued(job_id)
#             except Exception as e:
#                 # update failed -> mark failed, consider deleting html or leaving for cleanup
#                 await self.job_repo.mark_job_failed(job_id, f"db_update_failed: {e}")
#                 # optionally schedule deletion or add to orphan_files - repo can handle that
#                 return error_response(code=500, error_message=f"Failed to update job details: {str(e)}")

#             # 7) enqueue to redis stream (dispatcher handles normalization)
#             task_id = ulid.new().str
#             stream_fields = {
#                 "task_id": task_id,
#                 "job_id": job_id,
#                 "user_id": str(user_id),
#                 "html_gridfs_id": html_gridfs_id,
#                 "type": "png",
#                 "renderer_options": json.dumps(renderer_options),
#                 "created_at": datetime.utcnow().isoformat()
#             }
#             try:
#                 await self.dispatcher.enqueue(stream_fields)
#             except Exception as e:
#                 # enqueue failed -> mark job failed
#                 await self.job_repo.mark_job_failed(job_id, f"dispatch_failed: {e}")
#                 return error_response(code=500, error_message=f"Failed to enqueue render task: {str(e)}")

#             # 8) success
#             return success_response(code=202, data={"job_id": job_id, "task_id": task_id, "status": "queued"})


#         except HTTPException:
#             raise
#         except Exception as e:
#             # generic error
#             return error_response(code=500, error_message=f"Image rendering queue error: {str(e)}")
        
# async def generate_pdf_and_store(self, user_id: int):
#         try:
#             header_id = await self.header_repo.get_header_id_by_user_id(user_id)
#             if not header_id:
#                 raise HTTPException(status_code=404, detail="No header associated with this user")

#             user_data = await self.resume_repo.get_user_by_header_id(header_id)
#             html_content = self.html_renderer.render(user_data)
#             pdf_bytes = self.pdf_generator.generate(html_content)

#             metadata = {
#                 "user_id": user_id,
#                 "resume_name": user_data.get("full_name", "Generated_CV"),
#                 "uploaded_at": datetime.utcnow()
#             }

#             file_id = await self.storage.upload_pdf(
#                 f"{metadata['resume_name']}.pdf",
#                 pdf_bytes,
#                 metadata
#             )

#             return StreamingResponse(
#                 io.BytesIO(pdf_bytes),
#                 media_type="application/pdf",
#                 headers={
#                     "Content-Disposition": f"attachment; filename={metadata['resume_name']}.pdf",
#                     "X-File-ID": str(file_id)
#                 }
#             )

#         except Exception as e:
#             return error_response(code=500, error_message=f"PDF generation error: {str(e)}")

# async def generate_docx(self, user_id: int):
#         try:
#             header_id = await self.header_repo.get_header_id_by_user_id(user_id)
#             if not header_id:
#                 raise HTTPException(status_code=404, detail="No header associated with this user")

#             user_data = await self.resume_repo.get_user_by_header_id(header_id)
#             html_content = self.html_renderer.render(user_data)
#             docx_buffer = await self.docx_generator.generate_from_html(html_content)

#             return StreamingResponse(
#                 docx_buffer,
#                 media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
#                 headers={"Content-Disposition": f"attachment; filename={user_data.get('full_name', 'Generated_CV')}.docx"}
#             )

#         except Exception as e:
#             return error_response(code=500, error_message=f"DOCX generation error: {str(e)}")



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
