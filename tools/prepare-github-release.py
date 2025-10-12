import datetime
import subprocess
import sys
from pathlib import Path
from typing import Any
from typing import Iterable
from typing import List
from typing import Optional

import click
import github3
from github_app_auth import (
    GitHubAppAuthenticationError,
    get_installation_token,
    load_private_key,
)


def git(*args: str) -> str:
    try:
        process = subprocess.run(
            ["git", *args], check=True, capture_output=True, text=True
        )
        return process.stdout
    except subprocess.CalledProcessError as error:
        print(error.stdout, end="")
        print(error.stderr, end="", file=sys.stderr)
        raise


def replace_text(path: Path, old: str, new: str):
    text = path.read_text()
    text = text.replace(old, new)
    path.write_text(text)


def prepare_release(
    *,
    owner: str,
    repository_name: str,
    token: str,
    tag: str,
    remote: str,
    base: str,
    bump_paths: List[Path],
    label_names: List[str],
) -> None:
    branch = f"release-{tag}"
    title = f"Release {tag}"
    oldtag = git("describe", "--tags", "--abbrev=0").strip()

    git("switch", f"--create={branch}", base)

    for path in bump_paths:
        replace_text(path, oldtag, tag)
        git("add", str(path))

    git("commit", f"--message={title}")
    git("push", "--set-upstream", remote, branch)

    click.echo(f"pushed {branch}")

    github = github3.login(token=token)
    repository = github.repository(owner, repository_name)

    try:
        [release] = [release for release in repository.releases() if release.draft]
    except ValueError:
        raise RuntimeError("there should be exactly one draft release")

    pull_request = repository.create_pull(
        title=title,
        base=base,
        head=f"{owner}:{branch}",
        body=release.body,
    )

    click.echo(f"opened #{pull_request.number}")

    pull_request = repository.pull_request(pull_request.number)
    labels = pull_request.issue().add_labels(*label_names)

    for name in label_names:
        if name not in {label.name for label in labels}:
            raise RuntimeError(f"label {name} missing from #{pull_request.number}")

    click.echo(f"added labels {', '.join(label_names)} to #{pull_request.number}")


@click.command()
@click.option(
    "--owner",
    metavar="USER",
    required=True,
    envvar="GITHUB_ORGANIZATION",
    help="GitHub organization or GitHub username",
)
@click.option(
    "--repository",
    metavar="REPO",
    required=True,
    envvar="GITHUB_REPOSITORY",
    help="GitHub repository",
)
@click.option(
    "--remote",
    metavar="REMOTE",
    default="origin",
    help="remote for GitHub repository",
)
@click.option(
    "--base",
    metavar="BRANCH",
    default="main",
    help="default branch of the GitHub repository",
)
@click.option(
    "--bump",
    metavar="FILE",
    multiple=True,
    help="bump the version in these files (may be specified multiple times)",
)
@click.option(
    "labels",
    "--label",
    metavar="LABEL",
    multiple=True,
    help="labels for the pull request (may be specified multiple times)",
)
@click.option(
    "--app-id",
    metavar="APP_ID",
    required=True,
    envvar="GITHUB_APP_ID",
    help="GitHub App identifier",
)
@click.option(
    "--installation-id",
    metavar="INSTALLATION_ID",
    required=True,
    envvar="GITHUB_APP_INSTALLATION_ID",
    help="GitHub App installation identifier",
)
@click.option(
    "--private-key-path",
    type=click.Path(path_type=Path),
    envvar="GITHUB_APP_PRIVATE_KEY_PATH",
    help="Path to the GitHub App private key (PEM format)",
)
@click.option(
    "--private-key",
    envvar="GITHUB_APP_PRIVATE_KEY",
    help="GitHub App private key contents",
)
@click.argument("tag", required=False)
def main(
    owner: str,
    repository: str,
    remote: str,
    base: str,
    bump: Iterable[str],
    labels: Iterable[str],
    tag: Optional[str],
    app_id: str,
    installation_id: str,
    private_key_path: Optional[Path],
    private_key: Optional[str],
) -> None:
    """Open a pull request to release this project.

    If no release tag is specified, YYYY.MM.DD is used with the current date.
    There must be a single draft release. This script pushes a branch
    `release-TAG` and opens a pull request for it taking the pull request
    description from the draft release notes. The branch contains a single
    commit which updates the version number in the documentation.
    """

    if tag is None:
        today = datetime.date.today()
        tag = f"{today:%Y.%m.%d}".replace(".0", ".")

    try:
        installation_token = get_installation_token(
            app_id=app_id,
            installation_id=installation_id,
            private_key=load_private_key(
                private_key=private_key, private_key_path=private_key_path
            ),
        )

        prepare_release(
            owner=owner,
            repository_name=repository,
            token=installation_token,
            remote=remote,
            base=base,
            bump_paths=[Path(path) for path in bump],
            label_names=list(labels),
            tag=tag,
        )
    except (GitHubAppAuthenticationError, Exception) as error:
        click.secho(f"error: {error}", fg="red")
        sys.exit(1)


if __name__ == "__main__":
    main(prog_name="prepare-github-release")
