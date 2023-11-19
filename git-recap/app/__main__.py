"""Global starting point."""
import logging

from app import config
from app.lib import github_connector
from app.lib.recap import Client as RecapClient

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def main() -> None:
    """Start the application."""
    log.info('Start to recap...')
    settings = config.Settings()  # type: ignore
    github_connector_client = github_connector.Client(
        github_connector.create_github_client(settings.github_host, settings.github_token),
    )
    recap_client = RecapClient(github_connector_client)
    recap = recap_client.recap(exclude_repos=settings.repos_to_exclude)

    log.info(recap)


if __name__ == '__main__':  # pragma: no cover
    main()
