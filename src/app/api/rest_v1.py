import fastapi
import pydantic

from app.mongodb.repository import DataRepository

router = fastapi.APIRouter()


class BodyPayload(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="allow")


@router.get("")
async def get_collections(
    repository: DataRepository = fastapi.Depends(),
):
    return await repository.get_collections()


@router.delete("/{collection_name}", status_code=204)
async def delete_collection(
    collection_name: str = fastapi.Path(..., example="foobar"),
    repository: DataRepository = fastapi.Depends(),
):
    return await repository.delete_collection(collection_name)


@router.get("/{collection_name}")
async def get_collection(
    collection_name: str = fastapi.Path(..., example="foobar"),
    repository: DataRepository = fastapi.Depends(),
):
    return await repository.find(collection_name)


@router.get("/{collection_name}/{doc_id}")
async def get_document(
    doc_id: str,
    collection_name: str = fastapi.Path(..., example="foobar"),
    repository: DataRepository = fastapi.Depends(),
):
    return await repository.get_by_id(collection_name, doc_id)


@router.post("/{collection_name}", status_code=201)
async def create_document(
    collection_name: str = fastapi.Path(..., example="foobar"),
    payload: BodyPayload = fastapi.Body(),
    repository: DataRepository = fastapi.Depends(),
):
    return await repository.create(collection_name, payload.model_dump())


@router.patch("/{collection_name}/{doc_id}", status_code=204)
async def patch_document(
    doc_id: str,
    collection_name: str = fastapi.Path(..., example="foobar"),
    upsert: bool | None = fastapi.Query(None),
    payload: BodyPayload = fastapi.Body(),
    repository: DataRepository = fastapi.Depends(),
):
    return await repository.patch(collection_name, doc_id, payload.model_dump(), upsert)


@router.delete("/{collection_name}/{doc_id}", status_code=204)
async def delete_document(
    doc_id: str,
    collection_name: str = fastapi.Path(..., example="foobar"),
    repository: DataRepository = fastapi.Depends(),
):
    return await repository.delete_by_id(collection_name, doc_id)
