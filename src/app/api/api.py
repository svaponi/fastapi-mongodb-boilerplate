import fastapi

from . import rest_v1


def setup_api(app: fastapi.FastAPI):
    api_router = fastapi.APIRouter()
    api_router.include_router(rest_v1.router, prefix="/rest/v1", tags=["rest"])
    app.include_router(api_router, prefix="/api")
