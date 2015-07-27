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
        self.origin_size = 0
        self.size = 0
        self.status = -1
        self.progress = 0
        self.average_speed = 0
        self.time_left = 0
        self.pid_plowdown = 0
        self.pid_python = 0
        self.file_path = ''
        self.priority = 0
        self.infos_plowdown = ''
        self.lifecycle_insert_date = 0
        self.lifecycle_update_date = 0

    def to_string(self):
        return 'download : \n id => %s | name => %s | link => %s | origin_size => %s | size => %s' \
               ' | status => %s | progress => %s | average_speed => %s | time_left => %s | ' \
               'pid_plowdown => %s | pid_python => %s | file_path => %s | priority => %s' % (
                   str(self.id), self.name, self.link, str(self.origin_size), str(self.size), str(self.status), str(
                       self.progress), str(self.average_speed), str(self.time_left), str(self.pid_plowdown), str(
                       self.pid_python), self.file_path, str(self.priority))

        # + ' | lifecycle_insert_date => ' + str(self.lifecycle_insert_date)
        # + ' | lifecycle_update_date => ' + str(self.lifecycle_update_date)

