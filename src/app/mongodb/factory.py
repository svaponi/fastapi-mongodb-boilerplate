import os

from .handle import MongoHandle


def create_mongo() -> MongoHandle:
    mongo_uri = os.getenv("MONGO_URI")
    assert mongo_uri, "missing MONGO_URI"
    mongo_db = os.getenv("MONGO_DB")
    return MongoHandle(mongo_uri=mongo_uri, mongo_db=mongo_db)
