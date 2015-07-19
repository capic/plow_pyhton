__author__ = 'Vincent'


class Download:
    STATUS_WAITING = 1
    STATUS_IN_PROGRESS = 2
    STATUS_FINISHED = 3

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
        self.infos_plowdown = ''

    def to_string(self):
        return 'download : \n id => ' + str(self.id) + ' | name => ' + self.name \
               + ' | link => ' + self.link + ' | origin_size => ' + str(self.origin_size) + ' | size => ' \
               + str(self.size) + ' | status => ' + str(self.status) + ' | progress => ' + str(self.progress) \
               + ' | average_speed => ' + str(self.average_speed) + ' | time_left => ' + str(self.time_left) \
               + ' | pid_plowdown => ' + str(self.pid_plowdown) + ' | pid_python => ' + str(self.pid_python) \
               + '| file_path => ' + self.file_path