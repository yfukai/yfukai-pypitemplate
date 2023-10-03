# Major changes

This repo is a fork of [hypermodern python cookiecutter] and the major changes compared
to the hypermodern python cookiecutter are described on this page.

- Use [cruft] instead of [cookiecutter] to create instances of the template.
  _Cruft supports updating instances when the template is updated._
- Adopt template for use in Statistics Norway:
  - Template variables updated to support github_organization and copyright_owner.
  - Replace all references to cjolowicz-repos with ssb-pypitemplate.
- Replace use of [Read the Docs] with [GitHub Pages]. _One site less to register to._
- Add [SonarCloud] as a code quality analysis tool, including code coverage.
- Remove use of [CodeCov]. _One site less to register to and covered by SonarCloud._
- Support running `pytest` directly from the command line, without using `nox`.
- Replace flake8 and several other tools with [ruff] for linting.
- Add library function example.
  _The original template only had a command line tool example._
- Document generation works out of the box, even without `nox`.
  _Use `make html` in the docs directory._
- Fix warnings in GitHub Actions.

[codecov]: https://about.codecov.io/
[cookiecutter]: https://github.com/cookiecutter/cookiecutter
[cruft]: https://cruft.github.io/cruft/
[github pages]: https://docs.github.com/en/pages
[hypermodern python cookiecutter]: https://github.com/cjolowicz/cookiecutter-hypermodern-python
[read the docs]: https://readthedocs.org/
[ruff]: https://docs.astral.sh/ruff/
[sonarcloud]: https://www.sonarsource.com/products/sonarcloud/
