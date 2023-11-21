"""Module for github interactions."""
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from github import Github
from github.GithubException import GithubException
from github.Repository import Repository

log = logging.getLogger(__name__)


def create_github_client(github_host: str, github_token: str) -> Github:
    """Init the github client."""
    return Github(
        base_url='https://{0}/api/v3'.format(github_host),
        login_or_token=github_token,
    )


@dataclass
class Client(object):
    """Custom github client."""

    github_client: Github

    def get_commits(
        self,
        days: int,
        exclude_repos: list[str] = None,  # type: ignore
    ) -> list[dict[str, Any]]:
        """Get the commits from the past days."""
        if exclude_repos is None:
            exclude_repos = []  # type: ignore

        github_user = self.github_client.get_user()
        start_day = datetime.now() - timedelta(days=days)

        repository_commits = [
            _get_commits_from_repo(repo, github_user.login, start_day)
            for repo in github_user.get_repos()
            if not _is_repo_excluded(repo.full_name, exclude_repos)
        ]
        return [repo for repo in repository_commits if repo['commits']]


def _get_commits_from_repo(
    repository: Repository,
    github_username: str,
    start_day: datetime,
) -> dict[str, Any]:
    log.info('Get commits of repo: {0}'.format(repository.full_name))
    repo_info = {'repository': repository.full_name, 'commits': []}
    try:
        repo_info['commits'] = [
            {'message': commit.commit.message}  # type: ignore
            for commit in repository.get_commits(author=github_username, since=start_day)
        ]
    except GithubException as repo_exception:
        log.debug(
            'Cannot get commits of repository: {0}. Error: {1}'.format(
                repository.full_name, repo_exception,
            ),
        )
    return repo_info


def _is_repo_excluded(repository_fullname, exclude_patterns) -> bool:
    return any(re.match(pattern, repository_fullname) for pattern in exclude_patterns)
