import logging
import typing

import motor.motor_asyncio
from bson import ObjectId
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult


def create_motor_client(
    mongo_uri: str,
) -> motor.motor_asyncio.AsyncIOMotorClient:
    if not mongo_uri:
        raise ValueError("missing mongo_uri")
    return motor.motor_asyncio.AsyncIOMotorClient(mongo_uri)


MongoDocument = typing.Mapping[str, typing.Any]
MongoDocumentId = str | ObjectId


class MongoHandle:
    def __init__(
        self,
        mongo_uri: str,
        mongo_db: str = None,
        client: motor.motor_asyncio.AsyncIOMotorClient = None,
    ):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        client = client or create_motor_client(mongo_uri)
        self.db = client.get_database(mongo_db) if mongo_db else client.get_database()

    def get_collection(self, collection) -> motor.motor_asyncio.AsyncIOMotorCollection:
        return self.db.get_collection(collection)

    async def delete_collection(self, collection: str) -> None:
        res = await self.db.drop_collection(collection)
        self.logger.debug(f"drop_collection: {res}")

    async def find_one(
        self, collection: str, doc_id: MongoDocumentId
    ) -> MongoDocument | None:
        col = self.db.get_collection(collection)
        query = dict(_id=doc_id)
        res = await col.find_one(query)
        self.logger.debug(f"find_one: {res}")
        return res

    async def find(
        self,
        collection: str,
        **kwargs,
    ) -> list[MongoDocument]:
        col = self.db.get_collection(collection)
        cursor: motor.motor_asyncio.AsyncIOMotorCursor = col.find(kwargs)
        res = await cursor.to_list(None)
        self.logger.debug(f"find: {res}")
        return res

    async def insert_one(self, collection: str, doc: dict) -> MongoDocumentId:
        col = self.db.get_collection(collection)
        res: InsertOneResult = await col.insert_one(doc)
        self.logger.debug(f"insert_one: {res}")
        return res.inserted_id

    async def update_one(
        self,
        collection: str,
        doc_id: MongoDocumentId,
        doc: dict,
        upsert: bool = None,
    ) -> int:
        col = self.db.get_collection(collection)
        res: UpdateResult = await col.update_one(
            dict(_id=doc_id), {"$set": doc}, upsert=upsert or False
        )
        self.logger.debug(f"update_one: {res}")
        return res.modified_count

    async def delete_one(self, collection: str, doc_id: MongoDocumentId) -> int:
        col = self.db.get_collection(collection)
        query = dict(_id=doc_id)
        res: DeleteResult = await col.delete_one(query)
        self.logger.debug(f"delete_one: {res}")
        return res.deleted_count
