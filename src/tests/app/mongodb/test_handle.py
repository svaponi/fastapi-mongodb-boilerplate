import random
import uuid

import pytest

from app.mongodb.handle import MongoHandle


@pytest.mark.asyncio
async def test_crud(mongo_uri):

    test_collection = "test"
    mongo = MongoHandle(mongo_uri, "test")

    id1 = uuid.uuid4().hex
    id2 = uuid.uuid4().hex

    payload = dict(_id=id1, type="pizza", random=random.random())
    inserted_id = await mongo.insert_one(test_collection, payload)
    assert inserted_id == id1

    doc1 = await mongo.find_one(test_collection, id1)
    assert doc1.get("_id") == id1
    assert doc1.get("type") == "pizza"

    payload = dict(_id=id2, type="pizza", random=random.random())
    inserted_id = await mongo.insert_one(test_collection, payload)
    assert inserted_id == id2

    doc2 = await mongo.find_one(test_collection, id2)
    assert doc2.get("_id") == id2
    assert doc2.get("type") == "pizza"

    docs = await mongo.find(test_collection, type="pizza")
    assert len(docs) == 2

    payload = dict(type="ingredient")
    modified_count = await mongo.update_one(test_collection, id2, payload)
    assert modified_count == 1

    doc2_patched = await mongo.find_one(test_collection, id2)
    assert doc2_patched.get("_id") == id2
    assert doc2_patched.get("type") == "ingredient"
    assert doc2_patched.get("random") == doc2.get("random")

    docs = await mongo.find(test_collection, type="pizza")
    assert len(docs) == 1

    deleted_count = await mongo.delete_one(test_collection, id1)
    assert deleted_count == 1

    deleted_count = await mongo.delete_one(test_collection, id2)
    assert deleted_count == 1
