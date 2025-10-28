import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler


FORMATTER = logging.Formatter(
    '%(asctime)s %(levelname)s %(module)s %(funcName)s %(message)s'
)
LOG_FILE = os.getenv('LOG_FILE')
LOG_LEVEL: int | str = os.getenv('LOG_LEVEL', default=logging.ERROR)


def get_console_log_handler(log_level):
    console_log_handler = logging.StreamHandler(sys.stderr)
    console_log_handler.setFormatter(FORMATTER)
    console_log_handler.setLevel(log_level)
    return console_log_handler


def get_file_log_handler(log_file, log_level):
    file_log_handler = TimedRotatingFileHandler(
        filename=log_file,
        encoding='UTF-8',
        backupCount=7,
        when='midnight'
    )
    file_log_handler.setFormatter(FORMATTER)
    file_log_handler.setLevel(log_level)
    return file_log_handler


def get_logger(
    name: str,
) -> logging.Logger:
    logger = logging.getLogger(name=name)
    logger.addHandler(get_console_log_handler(LOG_LEVEL))
    if LOG_FILE:
        logger.addHandler(get_file_log_handler(LOG_FILE, LOG_LEVEL))
    logger.setLevel(LOG_LEVEL)
    return logger
