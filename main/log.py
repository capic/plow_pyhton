__author__ = 'Vincent'
import utils
import logging
import config
import time
import io
from http.client import HTTPConnection # py3
from service.logResource import LogResource


LEVEL_OFF = 0
LEVEL_ALERT = 1
LEVEL_ERROR = 2
LEVEL_INFO = 3
LEVEL_DEBUG = 4

import config
import sys

log_capture_string = io.StringIO()

def init(log_file_name):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(
        config.application_configuration.python_log_directory.path + log_file_name, 'w', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(config.application_configuration.python_log_format))
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(config.application_configuration.python_log_format))
    console_handler.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)

    # print("Prepare stream logger")
    # stream_handler = logging.StreamHandler(log_capture_string)
    # stream_handler.setFormatter(logging.Formatter(config.application_configuration.python_log_format))
    # stream_handler.setLevel(logging.DEBUG)
    # logger.addHandler(stream_handler)

    logging.getLogger("requests").setLevel(logging.WARNING)


def log(file_name, function_name, value, level, to_ihm=False, download=None):
    if config.application_configuration.python_log_level > LEVEL_OFF:

        if to_ihm is True:
            to_ihm_javascript_bool = 'true'
            if download is not None:
                LogResource.insert(download.id, value)
        else:
            to_ihm_javascript_bool = 'false'

        extra = {'file_name': file_name, 'function_name': function_name, 'to_ihm': to_ihm_javascript_bool}

        if level == LEVEL_ALERT:
            logging.critical(value, extra=extra)
        elif level == LEVEL_ERROR:
            logging.error(value, extra=extra)
        elif level == LEVEL_INFO:
            logging.info(value, extra=extra)
        elif level == LEVEL_DEBUG:
            logging.debug(value, extra=extra)

        # if to_ihm is True:
        #     if download is not None:
        #         log_contents = log_capture_string.getvalue()
        #         log_capture_string.close()
        #         print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA " + log_contents)
        #
        #
        #         LogResource.insert(download.id, value)

    # if config.application_configuration.python_log_console_level > LEVEL_OFF:
    #     if level <= config.application_configuration.python_log_console_level:
    #         l = ""
    #         if timetamp is True:
    #             l = l + time.strftime('%d/%m/%y %H:%M:%S', time.localtime()) + " "
    #
    #         l = l +value
    #         print(l)
