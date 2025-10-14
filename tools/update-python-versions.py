"""Update Python version pinning across the repository."""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path
from typing import Iterable, Sequence

MANIFEST_URL = (
    "https://raw.githubusercontent.com/actions/python-versions/main/versions-manifest.json"
)
SUPPORTED_COUNT = 4

REPO_ROOT = Path(__file__).resolve().parents[1]


def fetch_supported_python_versions() -> list[str]:
    """Fetch the manifest used by actions/setup-python and extract stable minors."""
    with urllib.request.urlopen(MANIFEST_URL, timeout=30) as response:  # noqa: S310
        manifest = json.load(response)

    minors: set[str] = set()
    for entry in manifest:
        if not entry.get("stable", False):
            continue
        version = entry["version"]
        major, minor, *_ = version.split(".")
        minors.add(f"{major}.{minor}")

    return sorted(minors, key=lambda item: tuple(int(part) for part in item.split(".")), reverse=True)[
        :SUPPORTED_COUNT
    ]


def format_list_literal(values: Iterable[str]) -> str:
    """Return a Python list literal with double-quoted string entries."""
    return "[" + ", ".join(f'"{value}"' for value in values) + "]"


def update_noxfile(path: Path, versions: list[str]) -> bool:
    """Update SUPPORTED_PYTHON_VERSIONS in a noxfile."""
    if not path.exists():
        return False

    pattern = re.compile(r'SUPPORTED_PYTHON_VERSIONS = \[[^\]]+\]')
    replacement = f'SUPPORTED_PYTHON_VERSIONS = {format_list_literal(versions)}'

    text = path.read_text()
    new_text, count = pattern.subn(replacement, text, count=1)

    if count and new_text != text:
        path.write_text(new_text)
        return True
    return False


def render_template_matrix(versions: list[str]) -> str:
    """Render the matrix include block for the template tests workflow."""
    latest = versions[0]
    mypy_versions = versions[:-1]
    tests_linux = versions

    lines = [
        f'          - {{ python: "{latest}", os: "ubuntu-latest", session: "pre-commit" }}',
    ]
    for version in mypy_versions:
        lines.append(f'          - {{ python: "{version}", os: "ubuntu-latest", session: "mypy" }}')
    for version in tests_linux:
        lines.append(f'          - {{ python: "{version}", os: "ubuntu-latest", session: "tests" }}')
    lines.extend(
        [
            f'          - {{ python: "{latest}", os: "windows-latest", session: "tests" }}',
            f'          - {{ python: "{latest}", os: "macos-latest", session: "tests" }}',
            f'          - {{ python: "{latest}", os: "ubuntu-latest", session: "typeguard" }}',
            f'          - {{ python: "{latest}", os: "ubuntu-latest", session: "xdoctest" }}',
            f'          - {{ python: "{latest}", os: "ubuntu-latest", session: "docs-build" }}',
        ]
    )
    return "\n".join(lines)


def render_root_matrix(versions: list[str]) -> str:
    """Render the matrix for the repository workflow."""
    latest = versions[0]
    lines = [
        f'          - {{ python-version: "{latest}", os: ubuntu-latest }}',
        f'          - {{ python-version: "{latest}", os: windows-latest }}',
        f'          - {{ python-version: "{latest}", os: macos-latest }}',
    ]
    for version in versions[1:]:
        lines.append(f'          - {{ python-version: "{version}", os: ubuntu-latest }}')
    return "\n".join(lines)


def replace_block(text: str, begin: str, end: str, replacement: str) -> tuple[str, bool]:
    """Replace the text between two sentinel comments (inclusive of sentinels)."""
    pattern = re.compile(
        rf"({re.escape(begin)}\n)(.*?)(\n\s*{re.escape(end)})",
        re.DOTALL,
    )
    new_text, count = pattern.subn(lambda match: f"{match.group(1)}{replacement}{match.group(3)}", text, count=1)
    return new_text, bool(count and new_text != text)


def update_template_tests_workflow(path: Path, versions: list[str]) -> bool:
    if not path.exists():
        return False

    text = path.read_text()
    matrix_block = render_template_matrix(versions)
    text, changed_matrix = replace_block(
        text,
        "          # python-versions-begin",
        "# python-versions-end",
        matrix_block,
    )
    latest = versions[0]
    text_new = re.sub(
        r'python-version: "\d+\.\d+"  # python-latest',
        f'python-version: "{latest}"  # python-latest',
        text,
    )
    changed_latest = text_new != text
    if changed_matrix or changed_latest:
        path.write_text(text_new)
    return changed_matrix or changed_latest


def update_root_tests_workflow(path: Path, versions: list[str]) -> bool:
    if not path.exists():
        return False

    text = path.read_text()
    matrix_block = render_root_matrix(versions)
    text, changed_matrix = replace_block(
        text,
        "          # python-versions-begin",
        "# python-versions-end",
        matrix_block,
    )
    latest = versions[0]
    text_new = re.sub(
        r'python-version: "\d+\.\d+"  # python-latest',
        f'python-version: "{latest}"  # python-latest',
        text,
    )
    changed_latest = text_new != text
    if changed_matrix or changed_latest:
        path.write_text(text_new)
    return changed_matrix or changed_latest


def update_versions(versions: list[str]) -> bool:
    """Update all files and return True if any changes were made."""
    changed = False
    for path in [
        REPO_ROOT / "noxfile.py",
        REPO_ROOT / "{{cookiecutter.project_name}}" / "noxfile.py",
    ]:
        if update_noxfile(path, versions):
            changed = True

    if update_template_tests_workflow(
        REPO_ROOT / "{{cookiecutter.project_name}}" / ".github" / "workflows" / "tests.yml",
        versions,
    ):
        changed = True

    if update_root_tests_workflow(
        REPO_ROOT / ".github" / "workflows" / "tests.yml",
        versions,
    ):
        changed = True

    return changed


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--print",
        action="store_true",
        help="Print the detected Python versions without mutating files.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    versions = fetch_supported_python_versions()

    if args.print:
        print(json.dumps(versions))
        return 0

    if update_versions(versions):
        print(f"Updated Python versions to: {', '.join(versions)}")
    else:
        print("Python versions already up to date.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
