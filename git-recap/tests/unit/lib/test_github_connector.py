from datetime import datetime
from unittest.mock import Mock

import pytest
from freezegun import freeze_time
from github.GithubException import GithubException

from app.lib import github_connector


@freeze_time('2023-11-01')
class TestGithubConnectorClient:

    @pytest.fixture(autouse=True, scope='function')
    def before_each(self):
        self.mock_github = Mock()

        self.test_repo_name_first = 'org1/repo1'
        self.test_repo_name_second = 'org2/repo2'
        self.test_commit_message_first = 'First commit'
        self.test_commit_message_second = 'Second commit'
        self.test_commit_message_third = 'Third commit'

        self.mock_repo_first = Mock(full_name=self.test_repo_name_first)
        self.mock_repo_first.get_commits.return_value = [
            Mock(commit=Mock(message=self.test_commit_message_first)),
            Mock(commit=Mock(message=self.test_commit_message_second)),
        ]

        self.mock_repo_second = Mock(full_name=self.test_repo_name_second)
        self.mock_repo_second.get_commits.return_value = [
            Mock(commit=Mock(message=self.test_commit_message_third)),
        ]

        self.mock_github_user = Mock()
        self.mock_github_user.login = 'test-user'
        self.mock_github_user.get_repos.return_value = [self.mock_repo_first, self.mock_repo_second]

        self.mock_github.get_user.return_value = self.mock_github_user

        self.github_connector_client = github_connector.Client(
            self.mock_github,
        )

    def test_get_yesterday_commits(self):
        commits = self.github_connector_client.get_commits(1)

        assert commits == [
            {
                'repository': self.test_repo_name_first,
                'commits': [
                    {'message': self.test_commit_message_first}, {'message': self.test_commit_message_second},
                ],
            },
            {
                'repository': self.test_repo_name_second,
                'commits': [{'message': self.test_commit_message_third}],
            },
        ]

        self.mock_repo_first.get_commits.assert_called_once_with(
            author='test-user',
            since=datetime(2023, 10, 31, 0, 0, 0),
        )
        self.mock_repo_second.get_commits.assert_called_once_with(
            author='test-user',
            since=datetime(2023, 10, 31, 0, 0, 0),
        )

    def test_empty_repo(self):
        self.mock_repo_first.get_commits.side_effect = GithubException(
            status=409, data={'message': 'Git Repository is empty.'},
        )

        commits = self.github_connector_client.get_commits(1)

        assert commits == [
            {
                'repository': self.test_repo_name_second,
                'commits': [{'message': self.test_commit_message_third}],
            },
        ]

    def test_exclude_repos_fullname(self):
        commits = self.github_connector_client.get_commits(1, exclude_repos=['org2/repo2'])

        assert commits == [
            {
                'repository': self.test_repo_name_first,
                'commits': [
                    {'message': self.test_commit_message_first}, {'message': self.test_commit_message_second},
                ],
            },
        ]

    def test_exclude_repos_pattern(self):
        commits = self.github_connector_client.get_commits(1, exclude_repos=['org2.*'])

        assert commits == [
            {
                'repository': self.test_repo_name_first,
                'commits': [
                    {'message': self.test_commit_message_first}, {'message': self.test_commit_message_second},
                ],
            },
        ]

    def test_do_not_include_repo_with_no_commits(self):
        self.mock_repo_second.get_commits.return_value = []

        commits = self.github_connector_client.get_commits(1)

        assert commits == [
            {
                'repository': self.test_repo_name_first,
                'commits': [
                    {'message': self.test_commit_message_first}, {'message': self.test_commit_message_second},
                ],
            },
        ]
