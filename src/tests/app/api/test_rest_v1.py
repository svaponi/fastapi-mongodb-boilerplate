import random
import uuid

import pytest


@pytest.mark.asyncio
async def test_crud(client):
    test_collection = f"test-{uuid.uuid4().hex}"

    payload = dict(type="pizza", random=random.random())
    res = client.post(f"/api/rest/v1/{test_collection}", json=payload)
    print(f"{res.url} >> {res.status_code} {res.text}")
    id1 = res.json()
    assert res.status_code == 201

    res = client.get(f"/api/rest/v1/{test_collection}/{id1}")
    print(f"{res.url} >> {res.status_code} {res.text}")
    assert res.status_code == 200
    assert res.json().get("type") == "pizza"

    res = client.get(f"/api/rest/v1/{test_collection}/non-existing")
    assert res.status_code == 404

    payload = dict(type="pizza", random=random.random())
    res = client.post(f"/api/rest/v1/{test_collection}", json=payload)
    print(f"{res.url} >> {res.status_code} {res.text}")
    id2 = res.json()
    assert res.status_code == 201

    res = client.get(f"/api/rest/v1/{test_collection}/{id2}")
    print(f"{res.url} >> {res.status_code} {res.text}")
    assert res.status_code == 200
    assert res.json().get("type") == "pizza"

    payload = dict(type="ingredient")
    res = client.patch(f"/api/rest/v1/{test_collection}/{id2}", json=payload)
    print(f"{res.url} >> {res.status_code} {res.text}")
    assert res.status_code == 204

    res = client.get(f"/api/rest/v1/{test_collection}/{id2}")
    print(f"{res.url} >> {res.status_code} {res.text}")
    assert res.status_code == 200
    assert res.json().get("type") == "ingredient"

    res = client.get(f"/api/rest/v1/{test_collection}")
    print(f"{res.url} >> {res.status_code} {res.text}")
    assert res.status_code == 200
    assert len(res.json().get("results")) == 2

    res = client.delete(f"/api/rest/v1/{test_collection}/{id1}")
    print(f"{res.url} >> {res.status_code} {res.text}")
    assert res.status_code == 204

    res = client.delete(f"/api/rest/v1/{test_collection}/{id2}")
    print(f"{res.url} >> {res.status_code} {res.text}")
    assert res.status_code == 204
