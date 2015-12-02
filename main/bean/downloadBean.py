# coding: utf8

__author__ = 'Vincent'

from datetime import datetime
from downloadDirectoryBean import DownloadDirectory
from downloadHostBean import DownloadHost


class Download:
    STATUS_WAITING = 1
    STATUS_IN_PROGRESS = 2
    STATUS_FINISHED = 3
    STATUS_ERROR = 4

    PRIORITY_NORMAL = 1

    def __init__(self):
        self.id = -1
        self.name = ''
        self.host = None
        self.package = None
        self.link = ''
        # the size of the file (values[1] gives by plowprobe or by the first rows of plowdown)
        self.size_file = 0
        # the size of the current download, equal to the size_file if the download has not been stop during previous download
        self.size_part = 0
        # the size downloaded, equal to the size_part_downloaded if the download has not been stop during previous download
        # otherwise the sum of size_file_downloaded and size_part_downloaded
        self.size_file_downloaded = 0
        # the size of the part downloaded
        self.size_part_downloaded = 0
        # the progress of the current part
        self.progress_part = 0
        self.status = 0
        self.average_speed = 0
        self.current_speed = 0
        self.time_spent = 0
        self.time_left = 0
        self.pid_plowdown = 0
        self.pid_python = 0
        self.directory = None
        self.to_move_directory = None
        self.file_path = ''
        self.priority = 0
        self.logs = ''
        self.theorical_start_datetime = None
        self.lifecycle_insert_date = None
        self.lifecycle_update_date = None

    def to_string(self):
        return 'download : \n id => %s | name => %s | host => %s | package => {%s} | link => %s | size_file => %s | size_part => %s' \
               ' | size_file_downloaded => %s | size_part_downloaded => %s' \
               ' | status => %s | progress_part => %s | average_speed => %s | current_speed => %s | time_left => %s ' \
               ' | time_spent => %s | pid_plowdown => %s | pid_python => %s  | directory => {%s} | | to_move_directory => {%s} | file_path => %s | priority => %s ' % (
                   str(self.id), self.name, self.host.to_string() if self.host is not None else 'null',
                   self.package.to_string() if self.package is not None else 'null', self.link, str(self.size_file),
                   str(self.size_part),
                   str(self.size_file_downloaded),
                   str(self.size_part_downloaded), str(self.status), str(self.progress_part), str(self.average_speed),
                   str(self.current_speed), str(self.time_left), str(self.time_spent), str(self.pid_plowdown),
                   str(self.pid_python), self.directory.to_string() if self.directory is not None else 'null',
                   self.to_move_directory.to_string() if self.to_move_directory is not None else 'null', self.file_path,
                   str(self.priority))

        # + ' | lifecycle_insert_date => ' + str(self.lifecycle_insert_date)
        # + ' | lifecycle_update_date => ' + str(self.lifecycle_update_date)

    def to_insert_json(self):
        return '{' \
               '"name": "%s", ' \
               '"host_id": %s, ' \
               '"package_id": %s, ' \
               '"link": "%s", ' \
               '"size_file": %s, ' \
               '"status": %s, ' \
               '"file_path": "%s", ' \
               '"priority": %s, ' \
               '"to_move_directory_id": %s, ' \
               '"lifecycle_insert_date": "%s", ' \
               '"lifecycle_update_date": "%s", ' \
               '"theorical_start_datetime": "%s"' \
               '}' % (
                   self.name,
                   self.host.id if self.host is not None else "null",
                   self.package.id if self.package is not None else "null",
                   self.link,
                   self.size_file,
                   self.status,
                   self.file_path,
                   self.priority,
                   self.to_move_directory.id if self.to_move_directory is not None else "null",
                   self.lifecycle_insert_date,
                   self.lifecycle_update_date,
                   self.theorical_start_datetime
               )

    def to_update_json(self):
        return {"download": '{"id": %s, '
                            '"name": "%s", '
                            '"host_id": %s, '
                            '"package_id": %s, '
                            '"link": "%s",'
                            '"size_file": %s, '
                            '"size_part": %s, '
                            '"size_file_downloaded": %s, '
                            '"size_part_downloaded": %s, '
                            '"status": %s, '
                            '"progress_part": %s, '
                            '"average_speed": %s, '
                            '"current_speed": %s, '
                            '"time_spent": %s, '
                            '"time_left": %s, '
                            '"pid_plowdown": %s, '
                            '"pid_python": %s, '
                            '"file_path": "%s", '
                            '"directory_id": %s, '
                            '"to_move_directory": %s, '
                            '"priority": %s, '
                            '"theorical_start_datetime": "%s", '
                            '"lifecycle_insert_date": "%s", '
                            '"lifecycle_update_date": "%s"}'
                            % (
                                self.id,
                                self.name,
                                self.host.id if self.host is not None else "null",
                                self.package.id if self.package is not None else "null",
                                self.link,
                                self.size_file,
                                self.size_part,
                                self.size_file_downloaded,
                                self.size_part_downloaded,
                                self.status,
                                self.progress_part,
                                self.average_speed,
                                self.current_speed,
                                self.time_spent,
                                self.time_left,
                                self.pid_plowdown,
                                self.pid_python,
                                self.file_path,
                                self.directory.id if self.directory is not None else "null",
                                self.to_move_directory.id if self.to_move_directory is not None else "null",
                                self.priority,
                                self.theorical_start_datetime,
                                self.lifecycle_insert_date,
                                self.lifecycle_update_date
                                )}

    def to_json(self):
        return '{' \
               '"id": %s, ' \
               '"name": "%s", ' \
               '"host": %s, ' \
               '"package": %s, ' \
               '"link": "%s", ' \
               '"size_file": %s, ' \
               '"size_part": %s, ' \
               '"size_file_downloaded": %s, ' \
               '"size_part_downloaded": %s, ' \
               '"status": %s, ' \
               '"progress_part": %s, ' \
               '"average_speed": %s, ' \
               '"current_speed": %s, ' \
               '"time_spent": %s, ' \
               '"time_left": %s, ' \
               '"pid_plowdown": %s, ' \
               '"pid_python": %s, ' \
               '"file_path": "%s", ' \
               '"directory": %s, ' \
               '"to_move_directory": %s, ' \
               '"priority": %s, ' \
               '"theorical_start_datetime": "%s", ' \
               '"lifecycle_insert_date": "%s", ' \
               '"lifecycle_update_date": "%s"' \
               '}' % (
                   self.id,
                   self.name,
                   self.host.to_json() if self.host is not None else "null",
                   self.package.to_json() if self.package is not None else "null",
                   self.link,
                   self.size_file,
                   self.size_part,
                   self.size_file_downloaded,
                   self.size_part_downloaded,
                   self.status,
                   self.progress_part,
                   self.average_speed,
                   self.current_speed,
                   self.time_spent,
                   self.time_left,
                   self.pid_plowdown,
                   self.pid_python,
                   self.file_path,
                   self.directory.to_json() if self.directory is not None else "null",
                   self.to_move_directory.to_json() if self.to_move_directory is not None else "null",
                   self.priority,
                   self.theorical_start_datetime,
                   self.lifecycle_insert_date,
                   self.lifecycle_update_date
               )
