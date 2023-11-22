from unittest import TestCase
from unittest.mock import Mock

from openai import OpenAI

from app.lib import ai_summarization


class TestCreateAIClient(TestCase):

    def test_create_ai_client(self):
        ai_client = ai_summarization.create_ai_client(Mock(spec=OpenAI))

        assert isinstance(ai_client, ai_summarization.OpenAIClient)

    def test_not_supported_client(self):
        with self.assertRaises(NotImplementedError):
            ai_summarization.create_ai_client(Mock())


class TestOpenAIClient(TestCase):

    def setUp(self):
        self.mock_ai_client = Mock()
        self.ai_summarization_client = ai_summarization.OpenAIClient(self.mock_ai_client)

    def test_take_any_argument(self):
        summary = self.ai_summarization_client.summarize([], {}, 'test', 123)

        assert summary == 'Summary'
