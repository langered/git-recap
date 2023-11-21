"""Recapitulation module."""
import logging
from dataclasses import dataclass

from app.lib.github_connector import Client as GithubConnectorClient

log = logging.getLogger(__name__)


@dataclass
class Client(object):
    """Client for recap operations."""

    github_client: GithubConnectorClient

    def recap(self, days: int = 1, exclude_repos: list[str] = None) -> str:  # type: ignore
        """Recap the work."""
        if exclude_repos is None:
            exclude_repos = []  # type: ignore
        commits = self.github_client.get_commits(days, exclude_repos=exclude_repos)
        log.info('Found number of commits: {0}'.format(len(commits)))

        issues = self.github_client.get_issues(days)
        log.info('Found created issues: {0}'.format(len(issues['created'])))
        log.info('Found commented issues: {0}'.format(len(issues['commented'])))

        return 'I have done everything.'
