from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION_PATTERN = re.compile(r"\d+(?:\.\d+)+")
SPECIFIER_PATTERN = re.compile(r"(>=|>|<=|<|==|!=)\s*(\d+(?:\.\d+)+)")
DOCKER_FROM_PATTERN = re.compile(
    r"^FROM\s+python:(\d+\.\d+)-slim\s+AS\s+(builder|runtime)\s*$",
    re.IGNORECASE | re.MULTILINE,
)


def version_tuple(value: str) -> tuple[int, ...]:
    if not VERSION_PATTERN.fullmatch(value):
        raise ValueError(f"Unsupported Python version format: {value!r}")
    return tuple(int(part) for part in value.split("."))


def is_allowed(version: tuple[int, ...], specifier: str) -> bool:
    clauses = [clause.strip() for clause in specifier.split(",")]
    for clause in clauses:
        match = SPECIFIER_PATTERN.fullmatch(clause)
        if match is None:
            raise ValueError(f"Unsupported requires-python clause: {clause!r}")

        operator, raw_bound = match.groups()
        bound = version_tuple(raw_bound)
        if operator == ">=" and not version >= bound:
            return False
        if operator == ">" and not version > bound:
            return False
        if operator == "<=" and not version <= bound:
            return False
        if operator == "<" and not version < bound:
            return False
        if operator == "==" and not version == bound:
            return False
        if operator == "!=" and version == bound:
            return False
    return True


def main() -> int:
    expected_text = (ROOT / ".python-version").read_text(encoding="utf-8").strip()
    expected = version_tuple(expected_text)
    errors: list[str] = []

    running = sys.version_info[: len(expected)]
    if running != expected:
        errors.append(
            f"CI interpreter is {'.'.join(map(str, running))}, but .python-version is {expected_text}."
        )

    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    workflow_versions = re.findall(r'^\s*python-version:\s*["\']?([0-9.]+)', workflow, re.MULTILINE)
    if expected_text not in workflow_versions:
        errors.append(
            f"CI setup-python version(s) {workflow_versions!r} do not include .python-version {expected_text}."
        )

    for dockerfile in (ROOT / "apps/api/Dockerfile", ROOT / "apps/worker/Dockerfile"):
        stages = DOCKER_FROM_PATTERN.findall(dockerfile.read_text(encoding="utf-8"))
        if [stage.lower() for _, stage in stages] != ["builder", "runtime"]:
            errors.append(f"{dockerfile.relative_to(ROOT)} must define Python builder and runtime stages.")
        for image_version, stage in stages:
            if image_version != expected_text:
                errors.append(
                    f"{dockerfile.relative_to(ROOT)} {stage} stage uses Python {image_version}; "
                    f"expected {expected_text} from .python-version."
                )

    for relative_path in ("apps/api/pyproject.toml", "apps/worker/pyproject.toml"):
        project = tomllib.loads((ROOT / relative_path).read_text(encoding="utf-8"))
        specifier = project["project"]["requires-python"]
        if not is_allowed(expected, specifier):
            errors.append(
                f".python-version {expected_text} is outside {relative_path} requires-python {specifier!r}."
            )

    lock = tomllib.loads((ROOT / "uv.lock").read_text(encoding="utf-8"))
    lock_specifier = lock["requires-python"]
    if not is_allowed(expected, lock_specifier):
        errors.append(f".python-version {expected_text} is outside uv.lock requires-python {lock_specifier!r}.")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(
        f"Python runtime alignment OK: Python {expected_text} matches CI, API/worker Dockerfiles, "
        "project metadata and uv.lock."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
