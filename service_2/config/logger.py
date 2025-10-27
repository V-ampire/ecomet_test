import logging
import pathlib
import sys
from logging.handlers import TimedRotatingFileHandler


FORMATTER = logging.Formatter(
    '%(asctime)s %(levelname)s %(module)s %(funcName)s %(message)s'
)


def get_console_log_handler(log_level: int | str = logging.ERROR):
    console_log_handler = logging.StreamHandler(sys.stderr)
    console_log_handler.setFormatter(FORMATTER)
    console_log_handler.setLevel(log_level)
    return console_log_handler


def get_file_log_handler(log_file: pathlib.Path, log_level: int | str = logging.ERROR):
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
    log_file: pathlib.Path | None = None,
    log_level: int | str = logging.ERROR
) -> logging.Logger:
    logger = logging.getLogger(name=name)
    logger.addHandler(get_console_log_handler(log_level))
    if log_file:
        logger.addHandler(get_file_log_handler(log_file=log_file, log_level=log_level))
    logger.setLevel(log_level)
    return logger
