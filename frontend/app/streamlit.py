""" Module for streamlit. """

from streamlit.web import cli
from structlog import get_logger

from frontend.app import config, main


def init() -> None:
    """Entry point if called as an executable."""

    logger = get_logger()
    logger.info("Starting init from streamlit")

    main.init()

    # run streamlit
    cli.main_run(
        [
            "frontend/app/chat_app.py",
            "--server.address=0.0.0.0",
            f"--server.port={config.CONFIG.chat_app_port}",
            f"--server.baseUrlPath={config.CONFIG.chat_app_base_url_path}",
        ]
    )

    logger.info("Completed init from streamlit")


if __name__ == "__main__":
    init()
