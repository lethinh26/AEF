import pytest
from aeo_platform.object_store import validate_object_key


@pytest.mark.parametrize("key", ["../secret", "/absolute/path", "a/../../secret", "a\\b", ""])
def test_object_key_rejects_path_traversal(key: str) -> None:
    with pytest.raises(ValueError):
        validate_object_key(key)


def test_object_key_accepts_scoped_relative_key() -> None:
    assert validate_object_key("tenant-1/artifacts/report.json") == "tenant-1/artifacts/report.json"
