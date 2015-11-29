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
        self.host = DownloadHost()
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
        self.directory = DownloadDirectory()
        self.to_move_directory = DownloadDirectory()
        self.file_path = ''
        self.priority = 0
        self.logs = ''
        self.theorical_start_datetime = None
        self.lifecycle_insert_date = 0
        self.lifecycle_update_date = 0

    def to_string(self):
        return 'download : \n id => %s | name => %s | host => %s | package => {%s} | link => %s | size_file => %s | size_part => %s' \
               ' | size_file_downloaded => %s | size_part_downloaded => %s' \
               ' | status => %s | progress_part => %s | average_speed => %s | current_speed => %s | time_left => %s ' \
               ' | time_spent => %s | pid_plowdown => %s | pid_python => %s  | directory => {%s} | | to_move_directory => {%s} | file_path => %s | priority => %s ' % (
                   str(self.id), self.name, self.host.to_string(), self.package.to_string() if self.package is not None else 'null', self.link, str(self.size_file), str(self.size_part),
                   str(self.size_file_downloaded),
                   str(self.size_part_downloaded), str(self.status), str(self.progress_part), str(self.average_speed),
                   str(self.current_speed), str(self.time_left), str(self.time_spent), str(self.pid_plowdown),
                   str(self.pid_python), self.directory.to_string(), self.to_move_directory.to_string(), self.file_path, str(self.priority))

        # + ' | lifecycle_insert_date => ' + str(self.lifecycle_insert_date)
        # + ' | lifecycle_update_date => ' + str(self.lifecycle_update_date)

    def to_insert_json(self):
        return {"name": self.name,
                "host_id": self.host.id,
                "package_id": self.package.id if self.package is not None else None,
                "link": self.link,
                "size_file": self.size_file,
                "status": self.status,
                "file_path": self.file_path,
                "priority": self.priority,
                "to_move_directory_id": self.to_move_directory.id,
                "lifecycle_insert_date": self.lifecycle_insert_date,
                "lifecycle_update_date": self.lifecycle_update_date,
                "theorical_start_datetime": self.theorical_start_datetime
                }

    def to_json(self):
        return {"id": str(self.id),
                "name": self.name,
                "host": self.host.to_json(),
                "package": self.package.to_json() if self.package is not None else None,
                "link": self.link,
                "size_file": str(self.size_file),
                "size_part": str(self.size_part),
                "size_file_downloaded": str(self.size_file_downloaded),
                "size_part_downloaded": str(self.size_part_downloaded),
                "status": str(self.status),
                "progress_part": str(self.progress_part),
                "average_speed": str(self.average_speed),
                "current_speed": str(self.current_speed),
                "time_spent": str(self.time_spent),
                "time_left": str(self.time_left),
                "pid_plowdown": str(self.pid_plowdown),
                "pid_python": str(self.pid_python),
                "file_path": str(self.file_path),
                "directory": self.directory.to_json(),
                "to_move_directory": self.to_move_directory.to_json(),
                "priority": str(self.priority),
                "theorical_start_datetime": str(self.theorical_start_datetime),
                "lifecycle_insert_date": str(self.lifecycle_insert_date),
                "lifecycle_update_date": str(self.lifecycle_update_date)
                }
