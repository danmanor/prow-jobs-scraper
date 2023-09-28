import logging


def get_logger(log_level: str) -> logging.Logger:
    """
    Args:
        log_level: log level

    Returns:
        formatted logger with log-level.
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level.upper())
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(stream_handler)

    return logger
