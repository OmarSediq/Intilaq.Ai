# from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorGridFSBucket
# from fastapi import UploadFile
# from fastapi.responses import StreamingResponse
# from bson import ObjectId
# from datetime import datetime
# from io import BytesIO
# from typing import Optional, Union

# class ResumeGridFSRepository:
#     def __init__(self, bucket: AsyncIOMotorGridFSBucket , db: Optional[AsyncIOMotorDatabase] = None):
#         self.fs = bucket
#         self.db = db 

#     async def save_pdf(self, file: UploadFile, user_id: str, resume_name: str):
#         content = await file.read()
#         metadata = {
#             "user_id": user_id,
#             "resume_name": resume_name,
#             "uploaded_at": datetime.utcnow()
#         }
#         # returns Inserted file id (ObjectId)
#         return await self.fs.upload_from_stream(file.filename, content, metadata=metadata)

#     async def get_pdf(self, file_id: str):
#         # this keeps your original method name and behavior
#         stream = await self.fs.open_download_stream(ObjectId(file_id))
#         content = await stream.read()  # NOTE: small files ok — streaming alternative possible
#         return StreamingResponse(BytesIO(content), media_type="application/pdf")
