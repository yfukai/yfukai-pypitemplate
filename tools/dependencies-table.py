import re
from pathlib import Path

import tomli


PROJECT = Path("{{cookiecutter.project_name}}")
JINJA_PATTERN = re.compile(r"{%.*%}")
JINJA_PATTERN2 = re.compile(r"{{[^{]*}}")
LINE_FORMAT = "   {name:{width}} {description}"
CANONICALIZE_PATTERN = re.compile(r"[-_.]+")
DESCRIPTION_PATTERN = re.compile(r"\. .*")
REQUIREMENT_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+")


def canonicalize_name(name: str) -> str:
    # From ``packaging.utils.canonicalize_name`` (PEP 503)
    return CANONICALIZE_PATTERN.sub("-", name).lower()


def truncate_description(description: str) -> str:
    """Truncate the description to the first sentence."""
    return DESCRIPTION_PATTERN.sub(".", description)


def format_dependency(dependency: str) -> str:
    """Format the dependency for the table."""
    return "coverage__" if dependency == "coverage" else f"{dependency}_"


def extract_requirement_name(requirement: str) -> str:
    """Extract the package name from a dependency specification string."""
    requirement = requirement.strip().strip('"').strip("'")
    requirement = requirement.split("[", 1)[0]
    match = REQUIREMENT_PATTERN.match(requirement)
    if match is None:  # pragma: no cover - defensive
        raise ValueError(f"cannot parse requirement name from '{requirement}'")
    return match.group(0)


def main() -> None:
    """Print restructuredText table of dependencies."""
    path = PROJECT / "pyproject.toml"
    text = path.read_text()
    text = JINJA_PATTERN.sub("", text)
    text = JINJA_PATTERN2.sub("x", text)
    data = tomli.loads(text)

    dependencies = {
        canonicalize_name(extract_requirement_name(requirement))
        for requirement in data.get("dependency-groups", {}).get("dev", [])
    }

    path = PROJECT / "uv.lock"
    if not path.exists():  # pragma: no cover - convenience for maintainers
        raise FileNotFoundError(
            "uv.lock not found. Run 'uv lock' in the project directory first."
        )
    text = path.read_text()
    data = tomli.loads(text)

    descriptions = {
        canonicalize_name(package["name"]): truncate_description(package["description"])
        for package in data["package"]
        if package["name"] in dependencies
    }

    table = {
        format_dependency(dependency): descriptions[dependency]
        for dependency in sorted(dependencies)
    }

    width = max(len(name) for name in table)
    width2 = max(len(description) for description in table.values())
    separator = LINE_FORMAT.format(
        name="=" * width, width=width, description="=" * width2
    )

    print(separator)

    for name, description in table.items():
        line = LINE_FORMAT.format(name=name, width=width, description=description)

        print(line)

    print(separator)


if __name__ == "__main__":
    main()
