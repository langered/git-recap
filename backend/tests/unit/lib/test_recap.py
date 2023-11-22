from unittest.mock import Mock

import pytest

from app.lib import recap


class TestRecapClient:
    @pytest.fixture(autouse=True, scope='function')
    def before_each(self):
        self.mock_github_connector_client = Mock()
        self.mock_github_connector_client.get_commits.return_value = []
        self.mock_github_connector_client.get_issues.return_value = {'created': [], 'commented': []}
        self.recap_client = recap.Client(
            self.mock_github_connector_client,
        )

    def test_recap(self):
        recap_text = self.recap_client.recap()

        assert recap_text == 'I have done everything.'

        self.mock_github_connector_client.get_commits.assert_called_once_with(1, exclude_repos=[])
