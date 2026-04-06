
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

        