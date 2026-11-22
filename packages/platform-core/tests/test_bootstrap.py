import pytest
from aeo_platform.bootstrap import parse_repository_slug


def test_parse_repository_slug() -> None:
    assert parse_repository_slug("lethinh26/Clucky") == ("lethinh26", "Clucky")


@pytest.mark.parametrize("value", ["owner", "owner/repo/extra", "../repo", "owner/../repo"])
def test_parse_repository_slug_rejects_invalid_values(value: str) -> None:
    with pytest.raises(ValueError):
        parse_repository_slug(value)
