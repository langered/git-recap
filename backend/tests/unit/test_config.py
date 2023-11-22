import os

import pytest

from app import config


class TestConfig:

    @pytest.fixture(autouse=True, scope='function')
    def before_each(self):
        os.environ.pop('GITHUB_HOST', None)
        os.environ.pop('GITHUB_TOKEN', None)
        os.environ.pop('RECAP_DAYS', None)

    def test_default_settings(self):
        config.Settings()  # type: ignore

    def test_overwrite_days(self):
        os.environ['GITHUB_API'] = 'https://github.example.com'
        os.environ['GITHUB_TOKEN'] = 'secret-token'
        os.environ['RECAP_DAYS'] = '2'

        settings = config.Settings()  # type: ignore

        assert settings.github_api == 'https://github.example.com'
        assert settings.github_token == 'secret-token'
        assert settings.recap_days == 2
