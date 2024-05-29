# -*- coding: utf-8 -*-

"""SensingClues logging"""

import logging
import sys

DEFAULT_LOGGER_NAME = "SensingCluesLogger"
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_LOG_FORMAT = {
    "fmt": "{asctime:s} [{filename:s}:{lineno:d}] {levelname:s} - {message:s}",
    "style": "{",
    "datefmt": "%Y-%m-%d %H:%M:%S",
}


def get_sc_logger() -> logging.Logger:
    """Get the global SensingClues logger

    Returns
    -------
    sc_logger : logging.Logger
        SensingClues logger instance.
    """
    # get the SensingClues logger
    sc_logger = logging.getLogger(DEFAULT_LOGGER_NAME)

    # set log level
    sc_logger.setLevel(DEFAULT_LOG_LEVEL)

    if not sc_logger.hasHandlers():
        # sc_logger.propagate = 0

        # create logging formatter
        log_fmt = logging.Formatter(**DEFAULT_LOG_FORMAT)

        # create default handler
        def_hand = logging.StreamHandler(stream=sys.stdout)
        def_hand.setFormatter(log_fmt)
        sc_logger.addHandler(def_hand)

    return sc_logger


def set_sc_log_level(level: str = None):
    """Set the SensingClues log level

    If no level is supplied it will set the default log level.

    Parameters
    ----------
    level : str or None, optional
        Log level (default is `default_log_level` from SensingClues config).
    """
    if level:
        log_level = level

    # get the logger; this will automatically set the level from the config
    sc_logger = get_sc_logger()
    sc_logger.debug(f'{sc_logger.name} log level set to "{log_level}".')
