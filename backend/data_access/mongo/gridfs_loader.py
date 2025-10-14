import json
import asyncio
import inspect
import uuid
from typing import Optional, Dict, Any, Union, Tuple

from bson import ObjectId
from motor.motor_asyncio import (
    AsyncIOMotorGridOut,
    AsyncIOMotorGridFSBucket,
    AsyncIOMotorClient,
    AsyncIOMotorDatabase,
)

from backend.core.providers.infra_providers import get_mongo_client_raw, get_mongo_db

HR_DB_DEFAULT = "hr_db"


class GridFSLoader:
    """
    Class wrapper for GridFS JSON payload loading/saving.
    Original async functions are preserved.
    """

    async def _maybe_await(self, value):
        """
        If value is awaitable (coroutine or other awaitable), await it, else return directly.
        """
        if inspect.isawaitable(value):
            return await value
        return value

    async def _resolve_client_and_db(self, db_name: Optional[str] = None) -> Tuple[AsyncIOMotorClient, AsyncIOMotorDatabase]:
        """
        Returns tuple (client, db). Works whether infra providers return sync values or coroutines.
        """
        client_candidate = get_mongo_client_raw()
        client = await self._maybe_await(client_candidate)

        if db_name:
            db = client[db_name]
        else:
            db_candidate = get_mongo_db()
            db_or_coro = await self._maybe_await(db_candidate)
            if hasattr(db_or_coro, "get_collection"):
                db = db_or_coro
            else:
                db = db_or_coro[HR_DB_DEFAULT] if hasattr(db_or_coro, "__getitem__") else client[HR_DB_DEFAULT]

        return client, db

    async def load_json_from_gridfs_async(self, file_id: Union[str, ObjectId], db_name: Optional[str] = None) -> Dict[str, Any]:
        client, db = await self._resolve_client_and_db(db_name)
        bucket = AsyncIOMotorGridFSBucket(db)

        try:
            if isinstance(file_id, ObjectId):
                oid = file_id
            else:
                s = str(file_id).strip()
                if s.startswith("gridfs://"):
                    s = s.split("://", 1)[1]
                oid = ObjectId(s)
        except Exception as exc:
            raise ValueError(f"invalid file_id for GridFS: {file_id}") from exc

        file_doc = await db["fs.files"].find_one({"_id": oid})
        if not file_doc:
            raise FileNotFoundError(f"No GridFS file with _id={oid} in db={db.name}")

        content_type = file_doc.get("contentType", "") or ""
        filename = file_doc.get("filename", "") or ""

        looks_like_json = any(ct in content_type for ct in ("json", "application/json", "text/"))
        looks_like_json = looks_like_json or filename.lower().endswith(".json")

        if not looks_like_json:
            raise ValueError(
                f"GridFS file _id={oid} (filename={filename}, contentType={content_type}) "
                "does not look like JSON/text. Treat as binary."
            )

        stream: Optional[AsyncIOMotorGridOut] = None
        try:
            try:
                stream = await bucket.open_download_stream(oid)
            except Exception as exc:
                raise FileNotFoundError(f"GridFS open_download_stream failed for _id={oid}: {exc}") from exc

            raw_bytes = await stream.read()
            try:
                text = raw_bytes.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise UnicodeDecodeError(
                    "utf-8",
                    raw_bytes,
                    exc.start,
                    exc.end,
                    f"GridFS file _id={oid} (filename={filename}) is not valid UTF-8 JSON"
                ) from exc

            try:
                data = json.loads(text)
            except json.JSONDecodeError as exc:
                raise json.JSONDecodeError(
                    f"Invalid JSON in GridFS file _id={oid} (filename={filename}): {exc.msg}",
                    exc.doc,
                    exc.pos
                ) from exc

            if not isinstance(data, dict):
                raise ValueError(f"GridFS JSON payload for _id={oid} is not a JSON object/dict")

            return data

        finally:
            try:
                if stream is not None:
                    await stream.close()
            except Exception:
                pass

    async def save_json_to_gridfs_async(
        self,
        payload: Dict[str, Any],
        filename: Optional[str] = None,
        db_name: Optional[str] = None,
    ) -> str:
        client, db = await self._resolve_client_and_db(db_name)
        bucket = AsyncIOMotorGridFSBucket(db)

        text = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), default=str)
        data = text.encode("utf-8")

        fname = filename or f"payload_{uuid.uuid4().hex}.json"
        metadata = {"contentType": "application/json"}
        file_id = await bucket.upload_from_stream(fname, data, metadata=metadata)
        return str(file_id)

    async def get_json_by_file_id(self, file_id: Union[str, ObjectId]) -> Dict[str, Any]:
        """
        Return JSON object stored in GridFS.
        Raises ValueError if file is not valid JSON.
        """
        bucket = await self._get_bucket()
        try:
            oid = file_id if isinstance(file_id, ObjectId) else ObjectId(str(file_id))
        except Exception as exc:
            raise ValueError(f"invalid file_id: {file_id}") from exc

        grid_out: Optional[AsyncIOMotorGridOut] = None
        try:
            grid_out = await bucket.open_download_stream(oid)
            raw_bytes = await grid_out.read()
            text = raw_bytes.decode("utf-8")
            data = json.loads(text)
            if not isinstance(data, dict):
                raise ValueError(f"GridFS JSON payload for _id={oid} is not a JSON object/dict")
            return data
        finally:
            if grid_out is not None:
                await grid_out.close()

    async def _get_bucket(self) -> AsyncIOMotorGridFSBucket:
        """
        Helper to get GridFS bucket using resolved db.
        """
        _, db = await self._resolve_client_and_db()
        return AsyncIOMotorGridFSBucket(db)
