import pytest
from rest_framework.test import APIClient

r"""
Here we define common fixtures for all (or most) tests, like api_client that
is used in E2E tests.
"""


@pytest.fixture
def api_client():
    return APIClient
