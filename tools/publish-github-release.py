import datetime
import sys
from pathlib import Path
from typing import Optional

import click
import github3
from github_app_auth import (
    GitHubAppAuthenticationError,
    get_installation_token,
    load_private_key,
)


def publish_release(*, owner: str, repository_name: str, token: str, tag: str) -> None:
    github = github3.login(token=token)
    repository = github.repository(owner, repository_name)

    try:
        [pull_request] = list(repository.pull_requests(head=f"{owner}:release-{tag}"))
    except ValueError:
        raise RuntimeError(
            f"there should be exactly one pull request for {owner}:release-{tag}"
        )

    pull_request = repository.pull_request(pull_request.number)

    try:
        [*_, commit] = pull_request.commits()
    except ValueError:
        raise RuntimeError(
            f"there should be at least one commit associated with #{pull_request.number}"
        )

    try:
        [release] = [release for release in repository.releases() if release.draft]
    except ValueError:
        raise RuntimeError("there should be exactly one draft release")

    cs_state = commit.status().state
    # Allow pending state since the status always seems to be empty, hence state
    # pending, even if green checkmark on commit in GitHub web page.
    if cs_state != "success" and cs_state != "pending":
        raise RuntimeError(f"checks for #{pull_request.number} have failed: {cs_state}")

    if pull_request.is_merged():
        raise RuntimeError(f"#{pull_request.number} has been merged already")

    if not pull_request.mergeable:
        raise RuntimeError(f"#{pull_request.number} is not mergeable")

    title = f"{pull_request.title} (#{pull_request.number})"

    if not pull_request.merge(commit_title=title, merge_method="squash"):
        raise RuntimeError(f"cannot merge #{pull_request.number}")

    pull_request.refresh()

    if not pull_request.is_merged():
        raise RuntimeError(f"#{pull_request.number} was not merged")

    click.echo(f"merged #{pull_request.number}")

    branch = repository.ref(f"heads/{pull_request.head.ref}")

    if not branch.delete():
        raise RuntimeError(f"cannot remove {branch.ref}")

    click.echo(f"removed {branch.ref}")

    if not release.edit(
        tag_name=tag,
        name=tag,
        body=pull_request.body,
        draft=False,
        prerelease=False,
    ):
        raise RuntimeError(f"cannot publish {release.name}")

    click.echo(f"published {release.name}")


@click.command()
@click.option(
    "--owner",
    metavar="USER",
    required=True,
    envvar="GITHUB_ORGANIZATION",
    help="GitHub organization or GitHub user name",
)
@click.option(
    "--repository",
    metavar="REPO",
    required=True,
    envvar="GITHUB_REPOSITORY",
    help="GitHub repository",
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
    tag: Optional[str],
    app_id: str,
    installation_id: str,
    private_key_path: Optional[Path],
    private_key: Optional[str],
) -> None:
    """Publish a GitHub release for this project.

    If no release tag is specified, YYYY.MM.DD is used with the current date.
    There must be a single draft release, as well as a pull request for a
    branch `release-TAG`. This script merges the pull request and publishes
    the release, taking the release notes from the pull request description.
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

        publish_release(
            owner=owner,
            repository_name=repository,
            token=installation_token,
            tag=tag,
        )
    except (GitHubAppAuthenticationError, Exception) as error:
        click.secho(f"error: {error}", fg="red")
        sys.exit(1)


if __name__ == "__main__":
    main(prog_name="publish-github-release")
