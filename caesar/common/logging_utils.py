"""
logging_utils.py: Provides logging utility functions to project
"""

import logging
import logging.config


class LogUtils:

    @staticmethod
    def get_file_and_console_logger(name, mode):
        """
        Creates a logger that logs to the console and a file.
        :param name: The name of the logger.
        :param mode: The logging mode.
        :return: A logger instance.
        """
        filename = name + '.log'

        lg = logging.getLogger(name)
        fh = logging.FileHandler(filename, mode)
        ch = logging.StreamHandler()
        fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        fh.setFormatter(fmt)
        ch.setFormatter(fmt)

        lg.addHandler(fh)
        lg.addHandler(ch)
        lg.setLevel(logging.DEBUG)

        return lg
