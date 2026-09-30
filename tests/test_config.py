from pathlib import Path

import pytest

from pipeline.config import DATASETS, find_repo_root, load_settings


def test_repo_root_is_found_from_a_nested_directory(settings):
    nested = settings.data_dir.parent / "pipeline"
    assert find_repo_root(nested) == settings.data_dir.parent


def test_repo_root_error_explains_how_to_fix(tmp_path):
    with pytest.raises(FileNotFoundError, match="VIBECHECK_DATA_DIR"):
        find_repo_root(tmp_path)


def test_default_settings_point_at_committed_datasets(settings):
    for name in DATASETS:
        assert settings.dataset_path(name).is_file(), name
    assert settings.output_dir.name == "outputs"


def test_environment_overrides_paths(tmp_path):
    custom = load_settings(env={
        "VIBECHECK_DATA_DIR": str(tmp_path / "raw"),
        "VIBECHECK_OUTPUT_DIR": str(tmp_path / "out"),
    })
    assert custom.data_dir == (tmp_path / "raw").resolve()
    assert custom.output_dir == (tmp_path / "out").resolve()


def test_unknown_dataset_is_rejected(settings):
    with pytest.raises(KeyError, match="onboarding"):
        settings.dataset_path("payroll")


def test_dataset_path_supports_other_formats(settings):
    assert settings.dataset_path("onboarding", ".json") == Path(settings.data_dir, "onboarding.json")
