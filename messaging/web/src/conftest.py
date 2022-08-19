import os


import pytest
from test_plus import APITestCase


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
os.environ.setdefault("DJANGO_CONFIGURATION", os.environ.get("__ENV__"))

import configurations  # NOQA isort:skip

configurations.setup()


@pytest.fixture
def apitp(client):
    t = APITestCase()
    t.client = client
    return t


@pytest.fixture(scope="session")
def django_db_modify_db_settings():
    """Use the same database for all xdist processes"""
    pass
