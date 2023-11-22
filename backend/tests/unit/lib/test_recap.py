from typing import Any
from unittest.mock import Mock

import pytest

from app.lib import recap


class TestRecapClient:
    @pytest.fixture(autouse=True, scope='function')
    def before_each(self):
        self.mock_ai_client = Mock()
        self.mock_github_connector_client = Mock()
        self.commits: list[Any] = []
        self.issues: dict[str, Any] = {'created': [], 'commented': []}
        self.mock_summary = 'I have done everything.'
        self.mock_github_connector_client.get_commits.return_value = self.commits
        self.mock_github_connector_client.get_issues.return_value = self.issues
        self.mock_ai_client.summarize.return_value = self.mock_summary

        self.recap_client = recap.Client(
            self.mock_github_connector_client,
            self.mock_ai_client,
        )

    def test_recap(self):
        recap_text = self.recap_client.recap()

        assert recap_text == self.mock_summary

        self.mock_github_connector_client.get_commits.assert_called_once_with(1, exclude_repos=[])
        self.mock_ai_client.summarize.assert_called_once_with(self.commits, self.issues)
