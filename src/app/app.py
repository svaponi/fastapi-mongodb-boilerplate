import contextlib
import logging
import typing

import fastapi
from starlette.responses import RedirectResponse

from app.api.api import setup_api
from app.core.cors import setup_cors
from app.core.error_handlers import setup_error_handlers
from app.core.logs import setup_logging
from app.core.request_context import setup_request_context
from app.mongodb.factory import create_mongo


@contextlib.asynccontextmanager
async def _lifespan(app: "App"):
    app.logger.info(f"Starting 🔄")
    # ...
    app.logger.info("Started ✅ ")
    yield
    app.logger.info("Shutting down 🔄")
    # ...
    app.logger.info("Shutdown 🛑")


class App(fastapi.FastAPI):
    def __init__(
        self,
        **extra: typing.Any,
    ) -> None:
        # IMPORTANT all logs previous to calling setup_logging will be not formatted
        setup_logging()
        self.logger = logging.getLogger(f"app")

        super().__init__(lifespan=_lifespan, **extra)

        # RequestContext is a nice-to-have util that allows to access request related attributes anywhere in the code
        setup_request_context(self)

        # Http error handlers (equivalent to try block that can handle uncaught exceptions)
        setup_error_handlers(self)

        # Setup cors
        setup_cors(self)

        # Setup API routes
        setup_api(self)

        # We attach the MongoHandle to the app, so it can be reused for connection pooling.
        self.mongo = create_mongo()

        if hasattr(self, "docs_url") and self.docs_url:

            @self.get("/", include_in_schema=False)
            def root():
                return RedirectResponse(self.docs_url)


def create_app():
    return App()
