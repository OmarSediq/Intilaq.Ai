
from backend.data_access.mongo.home.gridfs_storage_repository import GridFSStorageRepository
from backend.data_access.mongo.home.cv_snapshot_repository import CVSnapshotRepository
from backend.data_access.mongo.home.user_cv_state_repository import UserCVStateRepository
class CVDownloadService:

    def __init__(self, snapshot_repo : CVSnapshotRepository, storage_repo : GridFSStorageRepository , user_cv_state_repo : UserCVStateRepository):
        self.snapshot_repo = snapshot_repo
        self.storage_repo = storage_repo
        self.user_cv_state_repo = user_cv_state_repo




    async def download_pdf(self, user_id: int) -> bytes:

        # 1️⃣ ensure user state exists
        await self.user_cv_state_repo.ensure_user_state(user_id)

        # 2️⃣ get current snapshot id
        snapshot_id = await self.user_cv_state_repo.get_current_snapshot_id(user_id)

        if not snapshot_id:
            raise ValueError("No current snapshot for this user")

        # 3️⃣ get snapshot
        snapshot = await self.snapshot_repo.get_snapshot(snapshot_id)

        if not snapshot:
            raise ValueError("Snapshot not found")

        # 🔒 security check (VERY IMPORTANT)
        if snapshot["user_id"] != user_id:
            raise ValueError("Unauthorized access to snapshot")

        # 4️⃣ get document id
        documents = snapshot.get("documents", {})

        pdf_id = documents.get("pdf")

        if not pdf_id:
            raise ValueError("PDF not generated yet")

        # 5️⃣ download from GridFS
        file_bytes = await self.storage_repo.download(pdf_id)

        return file_bytes

        
    async def review_html(self, user_id: int) -> bytes:

        # 1️⃣ ensure user state exists
        await self.user_cv_state_repo.ensure_user_state(user_id)

        # 2️⃣ get current snapshot id
        snapshot_id = await self.user_cv_state_repo.get_current_snapshot_id(user_id)

        if not snapshot_id:
            raise ValueError("No current snapshot for this user")

        # 3️⃣ get snapshot
        snapshot = await self.snapshot_repo.get_snapshot(snapshot_id)

        if not snapshot:
            raise ValueError("Snapshot not found")

        # 🔒 security check (VERY IMPORTANT)
        if snapshot["user_id"] != user_id:
            raise ValueError("Unauthorized access to snapshot")

        # 4️⃣ get document id
        documents = snapshot.get("documents", {})

        html_id = documents.get("html")

        if not html_id:
            raise ValueError("html not generated yet")

        # 5️⃣ download from GridFS
        file_bytes = await self.storage_repo.download(html_id)

        return file_bytes


    async def download_docx(self, user_id: int) -> bytes:

        # 1️⃣ ensure user state exists
        await self.user_cv_state_repo.ensure_user_state(user_id)

        # 2️⃣ get current snapshot id
        snapshot_id = await self.user_cv_state_repo.get_current_snapshot_id(user_id)

        if not snapshot_id:
            raise ValueError("No current snapshot for this user")

        # 3️⃣ get snapshot
        snapshot = await self.snapshot_repo.get_snapshot(snapshot_id)

        if not snapshot:
            raise ValueError("Snapshot not found")

        # 🔒 security check (VERY IMPORTANT)
        if snapshot["user_id"] != user_id:
            raise ValueError("Unauthorized access to snapshot")

        # 4️⃣ get document id
        documents = snapshot.get("documents", {})

        docx_id = documents.get("docx")

        if not docx_id:
            raise ValueError("PDF not generated yet")

        # 5️⃣ download from GridFS
        file_bytes = await self.storage_repo.download(docx_id)

        return file_bytes

    async def download_pdf_by_snapshot(self, snapshot_id: str, user_id: int):

        # 1️⃣ get snapshot
        snapshot = await self.snapshot_repo.get_snapshot(snapshot_id)

        if not snapshot:
            raise ValueError("Snapshot not found")

        if snapshot["user_id"] != user_id:
            raise ValueError("Unauthorized")

        # 2️⃣ get file_doc from GridFS
        file_doc = await self.storage_repo.get_file_by_snapshot(
            snapshot_id=snapshot_id,
            file_type="pdf"
        )

        file_id = file_doc["_id"]

        # 3️⃣ download
        return await self.storage_repo.download(file_id)

    async def download_by_file_id(self, file_id: str, user_id: int) -> bytes:

        # 1️⃣ get metadata
        file_doc = await self.storage_repo.get_file_metadata(file_id)

        metadata = file_doc.get("metadata", {})

        snapshot_id = metadata.get("snapshot_id")

        if not snapshot_id:
            raise ValueError("Invalid file metadata")

        # 2️⃣ get snapshot
        snapshot = await self.snapshot_repo.get_snapshot(snapshot_id)

        if not snapshot:
            raise ValueError("Snapshot not found")

        # 🔒 security
        if snapshot["user_id"] != user_id:
            raise ValueError("Unauthorized")

        # 3️⃣ download
        return await self.storage_repo.download(file_id)
            