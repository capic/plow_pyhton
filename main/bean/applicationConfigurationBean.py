__author__ = 'Vincent'

import json


class ApplicationConfiguration:
    def __init__(self):
        self.id_application = -1
        self.download_activated = True
        self.rest_address = ''
        self.notification_address = ''
        self.api_log_database_level = 0
        self.python_log_level = 0
        self.python_log_format = ''
        self.python_log_directory = None
        self.python_log_console_level = 0
        self.python_directory_download_temp = None
        self.python_directory_download = None
        self.python_directory_download_text = None

    def to_string(self):
        return 'id_application: %d | download_activated: %d | api_log_database_level: %d | python_log_level: %d | ' \
               'python_log_directory: %s | python_log_console_level: %d | python_directory_download_temp: %s | ' \
               'python_directory_download: %s' % (
                   self.id_application, self.download_activated, self.api_log_database_level, self.python_log_level,
                   self.python_log_directory.to_string() if self.python_log_directory is not None else 'null',
                   self.python_log_console_level,
                   self.python_directory_download_temp if self.python_directory_download_temp is not None else 'null',
                   self.python_directory_download if self.python_directory_download is not None else 'null'
               )
