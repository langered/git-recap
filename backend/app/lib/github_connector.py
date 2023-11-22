"""Module for github interactions."""
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from github import Github
from github.GithubException import GithubException
from github.Issue import Issue
from github.PaginatedList import PaginatedList
from github.Repository import Repository

log = logging.getLogger(__name__)

_GITHUB_TIME_FORMAT = '%Y-%m-%dT00:00:00Z'  # noqa: WPS323


def create_github_client(github_api: str, github_token: str) -> Github:
    """Init the github client."""
    return Github(
        base_url='https://{0}'.format(github_api),
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

    def get_issues(self, days: int) -> dict[str, Any]:
        """Get the issues from the past days."""
        end_date = datetime.now()
        end_date = end_date.replace(tzinfo=timezone.utc)
        start_date = end_date - timedelta(days=days)
        start_date = start_date.replace(tzinfo=timezone.utc)

        github_user = self.github_client.get_user()

        created_issues = self._search_created_issues(
            github_user.login,
            start_date.strftime(_GITHUB_TIME_FORMAT),
            end_date.strftime(_GITHUB_TIME_FORMAT),
        )
        commented_issues = self._search_issues_with_user_comments(github_user.login, start_date, end_date)

        return {
            'created': created_issues,
            'commented': commented_issues,
        }

    def _search_created_issues(self, username, start_date: str, end_date: str) -> list[dict[str, Any]]:
        issues = self.github_client.search_issues(
            'author:{username} created:{start_date}..{end_date}'.format(
                username=username,
                start_date=start_date,
                end_date=end_date,
            ),
        )

        return [_build_issue(issue) for issue in issues]

    def _search_issues_with_user_comments(
        self,
        username: str,
        start_date: datetime,
        end_date: datetime,
    ) -> list[dict[str, Any]]:
        issues = self.github_client.search_issues(
            'involves:{username} created:{start_date}..{end_date}'.format(
                username=username,
                start_date=start_date.strftime(_GITHUB_TIME_FORMAT),
                end_date=end_date.strftime(_GITHUB_TIME_FORMAT),
            ),
        )

        return _get_issues_with_user_comments(issues, username, start_date, end_date)


def _get_issues_with_user_comments(
    issues: PaginatedList[Issue],
    username: str,
    start_date: datetime,
    end_date: datetime,
) -> list[dict[str, Any]]:
    issues_with_user_comments = []
    for issue in issues:
        issue_dict = _build_issue(issue)
        comments = issue.get_comments()
        user_comments = [
            comment.body
            for comment in comments
            if comment.user.login == username and start_date <= comment.created_at <= end_date
        ]
        if user_comments:
            issue_dict['comments'] = user_comments
            issues_with_user_comments.append(issue_dict)

    return issues_with_user_comments


def _build_issue(issue: Issue) -> dict[str, Any]:
    return {
        'title': issue.title,
        'body': issue.body,
        'url': issue.html_url,
    }


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
