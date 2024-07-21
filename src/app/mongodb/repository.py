import base64
import datetime
import uuid

import fastapi
import pydantic

from app.core.errors import NotFoundException
from .handle import MongoHandle, MongoDocument


class DocumentPayload(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="allow")
    id: str = pydantic.Field(alias="_id")
    created_at: datetime.datetime = pydantic.Field(alias="_created_at")
    last_modified_at: datetime.datetime = pydantic.Field(alias="_last_modified_at")


class FindResultPayload(pydantic.BaseModel):
    results: list[DocumentPayload]
    resume_token: str | None = None


def _decode_resume_token(cursor: str) -> datetime.datetime:
    last_modified_at = base64.urlsafe_b64decode(cursor.encode()).decode()
    last_modified_at = datetime.datetime.fromisoformat(last_modified_at)
    return last_modified_at


def _encode_resume_token(last_modified_at: datetime.datetime) -> str:
    last_modified_at = last_modified_at.isoformat()
    last_modified_at = base64.urlsafe_b64encode(last_modified_at.encode()).decode()
    return last_modified_at


def _build_resume_token(res: list[DocumentPayload]) -> str | None:
    if not res:
        return None
    return _encode_resume_token(res[-1].last_modified_at)


def _to_document(doc: MongoDocument) -> DocumentPayload:
    _id = doc.get("_id")
    if _id and not isinstance(_id, str):
        doc = dict(**doc)
        doc["_id"] = str(_id)
    return DocumentPayload(**doc)


class DataRepository:
    def __init__(self, req: fastapi.Request):
        super().__init__()
        self.mongo: MongoHandle = req.app.mongo

    async def get_collections(self) -> list[str]:
        return await self.mongo.db.list_collection_names()

    async def delete_collection(self, collection: str) -> None:
        await self.mongo.delete_collection(collection)

    async def get_or_none(self, collection: str, doc_id: str) -> DocumentPayload | None:
        doc = await self.mongo.find_one(collection, doc_id)
        return _to_document(doc) if doc else None

    async def get_by_id(self, collection: str, doc_id: str) -> DocumentPayload:
        doc = await self.get_or_none(collection, doc_id)
        if not doc:
            raise NotFoundException("resource not found")
        return doc

    async def find(
        self,
        collection: str,
        filters: dict = None,
        limit: int | None = None,
        resume_token: str | None = None,
        **kwargs,
    ) -> FindResultPayload:
        filters = filters or {}
        if resume_token:
            resume_token = _decode_resume_token(resume_token).isoformat()
            filters.update({"_last_modified_at": {"$gt": resume_token}})
        limit = limit or 100
        cursor = (
            self.mongo.db[collection]
            .find(filters, **kwargs)
            .sort({"_last_modified_at": -1})
            .limit(limit)
        )
        res = await cursor.to_list(None)
        results = [_to_document(doc) for doc in res]
        return FindResultPayload(
            results=results,
            resume_token=_build_resume_token(results),
        )

    async def create(
        self,
        collection: str,
        doc: dict,
    ) -> str:
        doc["_id"] = uuid.uuid4().hex
        timestamp = datetime.datetime.now(datetime.UTC).isoformat()
        doc["_created_at"] = timestamp
        doc["_last_modified_at"] = timestamp
        inserted_id = await self.mongo.insert_one(collection, doc)
        return str(inserted_id)

    async def patch(
        self,
        collection: str,
        doc_id: str,
        doc: dict,
        upsert: bool = None,
    ) -> None:
        doc["_last_modified_at"] = datetime.datetime.now(datetime.UTC).isoformat()
        count = await self.mongo.update_one(collection, doc_id, doc, upsert)
        if not count:
            raise NotFoundException("resource not found")

    async def delete_by_id(
        self,
        collection: str,
        doc_id: str,
        raise_errors=False,
    ) -> None:
        count = await self.mongo.delete_one(collection, doc_id)
        if not count and raise_errors:
            raise NotFoundException("resource not found")
