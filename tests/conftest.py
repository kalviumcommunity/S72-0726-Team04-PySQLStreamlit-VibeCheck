import pytest

from pipeline.config import load_settings


@pytest.fixture(scope="session")
def settings():
    """Settings pointing at the real datasets committed under data/."""
    return load_settings(env={})
