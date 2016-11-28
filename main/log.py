__author__ = 'Vincent'
import utils
import logging
import logging.handlers
import config
import time
import io
from http.client import HTTPConnection # py3
from service.logResource import LogResource
import config
import sys


LEVEL_OFF = 0
LEVEL_ALERT = 1
LEVEL_ERROR = 2
LEVEL_INFO = 3
LEVEL_DEBUG = 4


stream_value = io.StringIO()


def init(log_file_name, download=None):
    logger_file = logging.getLogger('appli.file')
    logger_console = logging.getLogger('appli.console')
    logger_stream = logging.getLogger('appli.stream')

    logger_file.setLevel(logging.DEBUG)
    logger_console.setLevel(logging.DEBUG)
    logger_stream.setLevel(logging.DEBUG)

    if len(logger_file.handlers):
        print("Delete file handler")
        logger_file.handlers[0].stream.close()
        logger_file.removeHandler(logger_file.handlers[0])

    print("Init file handler => " + log_file_name)
    if download is None:
        file_handler = logging.FileHandler(
            config.application_configuration.python_log_directory.path + log_file_name, 'w', encoding='utf-8')
    else:
        file_handler = logging.FileHandler(
            config.application_configuration.python_log_directory.path + log_file_name % download.id, 'w',
            encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(config.application_configuration.python_log_format))
    logging.getLogger('appli.file').addHandler(file_handler)

    # if not len(logger_console.handlers):
    print('Init console handler')
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(config.application_configuration.python_log_format))
    console_handler.setLevel(logging.DEBUG)
    logger_console.addHandler(console_handler)

    if download is not None and not len(logger_stream.handlers):
        print('Init stream handler')
        stream_handler = logging.StreamHandler(stream_value)
        stream_handler.setFormatter(logging.Formatter(config.application_configuration.python_log_format))
        stream_handler.setLevel(logging.DEBUG)
        logger_stream.addHandler(stream_handler)

    logging.getLogger("requests").setLevel(logging.WARNING)
    print('Init finished')

def log(file_name, function_name, value, level, to_ihm=False, download=None):
    if config.application_configuration.python_log_level > LEVEL_OFF:
        if to_ihm is True:
            to_ihm_javascript_bool = 'true'
        else:
            to_ihm_javascript_bool = 'false'

        extra = {'file_name': file_name, 'function_name': function_name, 'to_ihm': to_ihm_javascript_bool}

        if level == LEVEL_ALERT:
            logging.getLogger('appli.file').critical(value, extra=extra)
            logging.getLogger('appli.console').critical(value, extra=extra)
            if to_ihm is True:
                logging.getLogger('appli.stream').critical(value, extra=extra)
        elif level == LEVEL_ERROR:
            logging.getLogger('appli.file').error(value, extra=extra)
            logging.getLogger('appli.console').error(value, extra=extra)
            if to_ihm is True:
                logging.getLogger('appli.stream').error(value, extra=extra)
        elif level == LEVEL_INFO:
            logging.getLogger('appli.file').info(value, extra=extra)
            logging.getLogger('appli.console').info(value, extra=extra)
            if to_ihm is True:
                logging.getLogger('appli.stream').info(value, extra=extra)
        elif level == LEVEL_DEBUG:
            logging.getLogger('appli.file').debug(value, extra=extra)
            logging.getLogger('appli.console').debug(value, extra=extra)
            if to_ihm is True:
                logging.getLogger('appli.stream').debug(value, extra=extra)

        if len(logging.getLogger('appli.stream').handlers) and download is not None and to_ihm is True:
            logging.getLogger('appli.stream').handlers[0].flush()
            stream_value.seek(0)
            LogResource.insert(download.id, stream_value.getvalue(), download.application_configuration_id)
            stream_value.truncate(0)
