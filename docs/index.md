# SSB PyPI Template

```{toctree}
---
hidden: true
maxdepth: 1
---

Quickstart <quickstart>
guide
contributing
Code of Conduct <codeofconduct>
license
Major changes <changes>
Changelog <https://github.com/yfukai/yfukai-pypitemplate/releases>
```

```{include} ../README.md
---
start-after: <!-- badges-begin -->
end-before: <!-- badges-end -->
---
```

[black badge]: https://img.shields.io/badge/code%20style-black-000000.svg
[black project]: https://github.com/psf/black
[calver badge]: https://img.shields.io/badge/calver-YYYY.MM.DD-22bfda.svg
[calver]: https://calver.org/
[code of conduct]: https://github.com/yfukai/yfukai-pypitemplate/blob/main/CODE_OF_CONDUCT.md
[codecov badge]: https://codecov.io/gh/statisticsnorway/ssb-pypitemplate/branch/main/graph/badge.svg
[codecov page]: https://app.codecov.io/gh/statisticsnorway/ssb-pypitemplate
[contributor covenant badge]: https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg
[github actions badge]: https://github.com/yfukai/yfukai-pypitemplate/workflows/Tests/badge.svg
[github actions page]: https://github.com/yfukai/yfukai-pypitemplate/actions?workflow=Tests
[github page]: https://github.com/yfukai/yfukai-pypitemplate
[license badge]: https://img.shields.io/github/license/statisticsnorway/ssb-pypitemplate
[license]: https://opensource.org/license/mit/
[pre-commit badge]: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
[pre-commit project]: https://pre-commit.com/
[python version badge]: https://img.shields.io/pypi/pyversions/ssb-pypitemplate-instance
[ruff badge]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
[ruff project]: https://github.com/astral-sh/ruff
[rtd badge]: https://readthedocs.org/projects/ssb-pypitemplate/badge/
[rtd page]: index
[status badge]: https://badgen.net/badge/status/stable/4bc51d

[Cookiecutter] template for a Python package
based on the [Hypermodern Python] article series,
and adopted for use in [Statistics Norway].

## Usage

Use [Cruft](https://cruft.github.io/cruft/) to create and update an instance of this template.

```console
cruft create https://github.com/yfukai/yfukai-pypitemplate.git --checkout=2025.7.18
```

To check if there are there are template updates and update your instance with
the new updates, run the following commands from the root directory:

```console
cruft check
cruft update
```

## Features

```{include} ../README.md
---
start-after: <!-- features-begin -->
end-before: <!-- features-end -->
---
```

## FAQ

### What is this project about?

The mission of this project is to
enable current best practices
through modern Python tooling.

### What makes this project different from other Python templates?

This is a general-purpose template for Python libraries and applications.

Our goals are:

- Focus on simplicity and minimalism
- Promote code quality through automation
- Provide reliable and repeatable processes

The project template is centered around the following tools:

- [uv][1] for packaging and dependency management
- [Nox][2] for automation of checks and other development tasks
- [GitHub Actions][3] for continuous integration and delivery

[1]: https://docs.astral.sh/uv/
[2]: https://nox.thea.codes/
[3]: https://github.com/features/actions
[cookiecutter]: https://github.com/cookiecutter/cookiecutter
[hypermodern python]: https://medium.com/@cjolowicz/hypermodern-python-d44485d9d769
[hypermodernism]: https://en.wikipedia.org/wiki/Hypermodernism_(chess)
[retrofuturism]: https://en.wikipedia.org/wiki/Retrofuturism
[statistics norway]: https://www.ssb.no/
