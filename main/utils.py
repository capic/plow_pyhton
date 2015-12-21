__author__ = 'Vincent'

import subprocess
import re

import psutil
from mysql.connector import (connection)
from bean.downloadBean import Download
from bean.downloadPackageBean import DownloadPackage
from bean.downloadDirectoryBean import DownloadDirectory
from bean.downloadHostBean import DownloadHost
from bean.actionBean import Action
import logging

REST_ADRESSE = 'http://localhost:3000/'

MYSQL_LOGIN = 'root'
MYSQL_PASS = 'capic_20_04_1982'
MYSQL_HOST = '192.168.1.101'
MYSQL_DATABASE = 'plowshare'

DIRECTORY_WEB_LOG = '.'
DIRECTORY_DOWNLOAD_DESTINATION_TEMP = '/mnt/HD/HD_a2/telechargement/temp_plowdown/'
DIRECTORY_DOWNLOAD_DESTINATION_ID = 1
DIRECTORY_DOWNLOAD_DESTINATION = '/mnt/HD/HD_a2/telechargement/'

LOG_OUTPUT = True
CONSOLE_OUTPUT = True

DEFAULT_UNIREST_TIMEOUT = 15


def database_connect():
    return connection.MySQLConnection(user=MYSQL_LOGIN, password=MYSQL_PASS, host=MYSQL_HOST, database=MYSQL_DATABASE)


def hms_to_seconds(t):
    log_debug(u'*** hms_to_seconds ***')

    if ':' in t:
        log_debug(u': in string')
        h, m, s = [int(i) for i in t.split(':')]
        d = 0
    elif 'd' in t:
        log_debug(u'd in string')
        m = 0
        s = 0
        log_debug(t.split())
        log_debug(t.split()[1])
        log_debug(t.split()[1].replace('h', ''))
        h = int(t.split()[1].replace('h', ''))
        log_debug(t.split())
        log_debug(t.split()[0])
        log_debug(t.split()[0].replace('d', ''))
        d = int(t.split()[0].replace('d', ''))

    return int(d * 24 * 3600 + 3600 * h + 60 * m + s)


def compute_size(s):
    if len(s) > 1:
        size_letter = s[-1:].lower()
        size_number = float(s[:-1])

        if size_letter == 'k':
            size_number *= 1024
        elif size_letter == 'm':
            size_number *= 1024 * 1024
    else:
        size_number = int(s)

    return int(size_number)


def kill_proc_tree(pid, including_parent=True):
    try:
        parent = psutil.Process(pid)
        for child in parent.children(recursive=True):
            child.kill()
        if including_parent:
            parent.kill()
    except psutil.NoSuchProcess:
        pass


def check_pid(pid):
    return psutil.pid_exists(pid)


def clean_plowdown_line(line):
    idxs = [m.start() for m in re.finditer('\[0', line)]

    n = 0
    if len(idxs) > 0:
        for idx in idxs:
            if idx == 1:
                if line[2] == ';':
                    n = 9
                    line = line[n:]
                else:
                    n = 7
                    line = line[n:]
            else:
                line = line[:idx - n]

    return line


def get_infos_plowprobe(cmd):
    log_debug(u'Command plowprobe %s' % cmd)
    output = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).communicate()[0].decode('UTF-8')

    if output.startswith('==>'):
        tab_infos = output.split('=$=')
        name = tab_infos[0].replace('==>', '')
        log_debug('name before modification %s' % name)
        name = clean_string_console(name)
        log_debug('name after modification %s' % name)

        size = 0
        if tab_infos[1] is not None and tab_infos[1] != '':
            size = int(tab_infos[1])
            log_debug(u'Size %s' % str(size))

        host = tab_infos[2]

        return [name, size, host]
    else:
        return [None, None]


def clean_string_console(string):
    string = string.strip()
    string = string.replace("\033\[[0-9;]+m", '')
    string = string.replace("\033", '')

    return string


def json_to_download_object(json_object):
    download = Download()
    download.id = json_object['id']
    download.name = json_object['name']
    if json_object['package_id']:
        download_package = DownloadPackage()
        download_package.id = json_object['download_package']['id']
        download_package.name = json_object['download_package']['name']
        download_package.unrar_progress = json_object['download_package']['unrar_progress']
    else:
        download_package = None
    download.package = download_package
    download.link = json_object['link']
    download.size_file = json_object['size_file']
    download.size_part = json_object['size_part']
    download.size_file_downloaded = json_object['size_file_downloaded']
    download.size_part_downloaded = json_object['size_part_downloaded']
    download.status = json_object['status']
    download.progress_part = json_object['progress_part']
    download.average_speed = json_object['average_speed']
    download.current_speed = json_object['current_speed']
    download.time_spent = json_object['time_spent']
    download.time_left = json_object['time_left']
    download.pid_plowdown = json_object['pid_plowdown']
    download.pid_python = json_object['pid_python']
    if json_object['directory_id']:
        download_directory = json_to_download_directory_object(json_object['directory'])
    else:
        download_directory = None
    download.directory = download_directory
    download.file_path = json_object['file_path']
    download.priority = json_object['priority']
    if json_object['theorical_start_datetime'] == 0:
        download.theorical_start_datetime = None
    else:
        download.theorical_start_datetime = json_object['theorical_start_datetime']
    if json_object['lifecycle_insert_date'] == 0:
        download.lifecycle_insert_date = None
    else:
        download.lifecycle_insert_date = json_object['lifecycle_insert_date']
    if json_object['lifecycle_update_date'] == 0:
        download.lifecycle_update_date = None
    else:
        download.lifecycle_update_date = json_object['lifecycle_update_date']

    return download


def json_to_download_object_list(json_array):
    list_downloads = []

    for json_object in json_array:
        download = json_to_download_object(json_object)
        list_downloads.append(download)

    return list_downloads


def json_to_download_package_object(json_object):
    download_package = DownloadPackage()
    download_package.id = json_object['id']
    download_package.name = json_object['name']
    download_package.unrar_percent = json_object['unrar_progress']

    return download_package


def json_to_download_directory_object(json_object):
    download_directory = DownloadDirectory()
    download_directory.id = json_object['id']
    download_directory.path = json_object['path']

    return download_directory


def json_to_action_object(json_object):
    action = Action()
    action.download_id = json_object['download_id']
    action.action_type_id = json_object['action_type_id']
    action.property_id = json_object['property_id']
    action.num = json_object['num']
    action.property_value = json_object['property_value']
    action.lifecycle_insert_date = json_object['lifecycle_insert_date']
    action.lifecycle_update_date = json_object['lifecycle_update_date']
    action.action_status_id = json_object['action_status_id']
    if json_object['directory_id']:
        directory = json_to_download_directory_object(json_object['directory'])
    else:
        directory = None
    action.directory = directory

    return action


def json_to_action_object_list(json_array):
    list_actions = []

    for json_object in json_array:
        action = json_to_action_object(json_object)
        list_actions.append(action)

    return list_actions


def json_to_download_host_object(json_object):
    download_host = DownloadHost()
    download_host.id = json_object['id']
    download_host.name = json_object['name']

    return download_host


def package_name_from_download_name(download_name):
    ext = download_name.split(".")[-1]
    log_debug('Extensions %s ' % ext)
    if ext == 'rar':
        return download_name.split(".part")[0]
    else:
        return None


def get_action_by_property(actions_list, property_id):
    action_returned = None

    for action in actions_list:
        if action.property_id == property_id:
            action_returned = action
            break

    return action_returned


def log_debug(value):
    if LOG_OUTPUT:
        logging.debug(value)

    if CONSOLE_OUTPUT:
        print(value)


def find_this_process(process_name):
    log_debug(u'*** find_this_process ***')

    command = "ps -eaf | grep \"" + process_name + "\""
    log_debug(u'command: %s' % command)
    ps = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    output = ps.stdout.read()
    ps.stdout.close()
    ps.wait()
    return output


def is_this_running(process_name):
    log_debug(u'*** is_this_running ***')
    output = find_this_process(process_name)

    if re.search(process_name, output) is None:
        log_debug(u' ===> False')
        return False
    else:
        log_debug(u' ===> True')
        return True