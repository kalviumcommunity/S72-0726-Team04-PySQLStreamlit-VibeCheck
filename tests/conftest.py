import pytest

from pipeline.config import load_settings


@pytest.fixture(scope="session")
def settings():
    """Settings pointing at the real datasets committed under data/."""
    return load_settings(env={})


@pytest.fixture(scope="session")
def staged_engine(tmp_path_factory):
    """A throwaway SQLite database holding the four raw tables, as the team DB would."""
    from pipeline.db import get_engine, stage_tables
    from pipeline.schemas import load_frames

    path = tmp_path_factory.mktemp("sql") / "vibecheck.db"
    engine = get_engine(f"sqlite:///{path.as_posix()}")
    stage_tables(engine, load_frames())
    yield engine
    engine.dispose()
