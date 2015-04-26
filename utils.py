__author__ = 'Vincent'

import psutil
from mysql.connector import (connection)

MYSQL_LOGIN = 'root'
MYSQL_PASS = 'capic_20_04_1982'
MYSQL_HOST = '127.0.0.1'
MYSQL_DATABASE = 'plowshare'


def database_connect():
    return connection.MySQLConnection(user=MYSQL_LOGIN, password=MYSQL_PASS, host=MYSQL_HOST, database=MYSQL_DATABASE)


def hms_to_seconds(t):
    h, m, s = [int(i) for i in t.split(':')]
    return 3600*h + 60*m + s


def compute_size(s):
    size_letter = s[-1:].lower()
    size_number = s[:-1]

    if size_letter == 'k':
        size_number *= 100
    elif size_letter == 'm':
        size_number *= 1000

    return size_number


def kill_proc_tree(pid, including_parent=True):
    parent = psutil.Process(pid)
    for child in parent.children(recursive=True):
        child.kill()
    if including_parent:
        parent.kill()