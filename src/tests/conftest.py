import pytest
import pytest_httpserver
from starlette.testclient import TestClient
from testcontainers.mongodb import MongoDbContainer

from app.app import create_app
from tests.testutils.mock_environ import mock_environ
from tests.testutils.mock_server import MockServer


@pytest.fixture
def mongo_uri():
    with MongoDbContainer("mongo:latest", dbname="test") as mongo:
        yield mongo.get_connection_url()


@pytest.fixture
def app(mongo_uri):
    with mock_environ(MONGO_URI=mongo_uri, MONGO_DB="test"):
        app = create_app()
        yield app


@pytest.fixture
def client(app):
    with TestClient(app, base_url="http://localhost") as client:
        yield client


@pytest.fixture
def mock_server(httpserver: pytest_httpserver.HTTPServer):
    server = MockServer(httpserver)
    yield server
    server.clear()
