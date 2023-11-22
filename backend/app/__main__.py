"""Global starting point."""
import logging

from openai import OpenAI

from app import config
from app.lib import ai_summarization, github_connector
from app.lib.recap import Client as RecapClient

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def main() -> None:
    """Start the application."""
    log.info('Start to recap...')
    settings = config.Settings()  # type: ignore
    recap_client = RecapClient(
        github_connector.Client(
            github_connector.create_github_client(settings.github_api, settings.github_token),
        ),
        ai_summarization.create_ai_client(OpenAI(api_key=settings.openai_token)),
    )
    recap = recap_client.recap(exclude_repos=settings.repos_to_exclude)

    log.info(recap)


if __name__ == '__main__':  # pragma: no cover
    main()
