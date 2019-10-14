import logging.config

from src.paths import get_log_config_filepath

# Read config from file. This line must be run at all files being directly executed
logging.config.fileConfig(get_log_config_filepath(), disable_existing_loggers=False)

# This line must be added at the top level of each module
logger = logging.getLogger(__name__)


def main():
    logger.info("This is a message example")
    pass


if __name__ == "__main__":
    main()
