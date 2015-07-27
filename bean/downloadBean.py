__author__ = 'Vincent'


class Download:
    STATUS_WAITING = 1
    STATUS_IN_PROGRESS = 2
    STATUS_FINISHED = 3

    PRIORITY_NORMAL = 1

    def __init__(self):
        self.id = -1
        self.name = ''
        self.link = ''
        # the size of the file (values[1] gives by plowprobe or by the first rows of plowdown)
        self.size_file = 0
        # the size of the current download, equal to the size_file if the download has not been stop during previous download
        self.size_part = 0
        # the size downloaded, equal to the size_part_downloaded if the download has not been stop during previous download
        # otherwise the sum of size_file_downloaded and size_part_downloaded
        self.size_file_downloaded = 0
        # the size of the previous part, used to add the size_part_downloaded to have the size_file_downloaded
        self.size_previous_part_downloaded = 0
        # the size of the part downloaded
        self.size_part_downloaded = 0
        # the progress of the current part
        self.progress_part = 0
        self.status = 0
        self.average_speed = 0
        self.time_spent = 0
        self.time_left = 0
        self.pid_plowdown = 0
        self.pid_python = 0
        self.file_path = ''
        self.priority = 0
        self.infos_plowdown = ''
        self.lifecycle_insert_date = 0
        self.lifecycle_update_date = 0

    def to_string(self):
        return 'download : \n id => %s | name => %s | link => %s | size_file => %s | size_part => %s' \
               ' | size_file_downloaded => %s | size_previous_part_downloaded => %s | size_part_downloaded => %s' \
               ' | status => %s | progress_part => %s | average_speed => %s | time_left => %s | time_spent => %s' \
               'pid_plowdown => %s | pid_python => %s | file_path => %s | priority => %s' % (
                   str(self.id), self.name, self.link, str(self.size_file), str(self.size_part),
                   str(self.size_file_downloaded), str(self.size_previous_part_downloaded),
                   str(self.size_part_downloaded), str(self.status), str(self.progress_part), str(self.average_speed),
                   str(self.time_left), str(self.time_spent), str(self.pid_plowdown), str(self.pid_python),
                   self.file_path, str(self.priority))

        # + ' | lifecycle_insert_date => ' + str(self.lifecycle_insert_date)
        # + ' | lifecycle_update_date => ' + str(self.lifecycle_update_date)

