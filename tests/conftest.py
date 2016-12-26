import pytest
from bottleneck import clean_db

from bigleague.storage import get_tables
from bigleague.app import create_app_singletons


@pytest.yield_fixture
def db():
    tables = get_tables()
    clean_db(tables)
    try:
        yield
    finally:
        clean_db(tables)


@pytest.fixture
def app():
    app, _ = create_app_singletons()
    return app
