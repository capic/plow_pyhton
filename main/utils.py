__author__ = 'Vincent'

import subprocess
import re

import psutil
from mysql.connector import (connection)
from bean.downloadBean import Download
from bean.downloadPackageBean import DownloadPackage
from bean.downloadDirectoryBean import DownloadDirectory
from bean.downloadHostBean import DownloadHost
from bean.applicationConfigurationBean import ApplicationConfiguration
from bean.actionBean import Action
from bean.propertyBean import Property
import logging
import os
import sys
import time
import json

# REST_ADRESSE = 'http://192.168.1.101:3000/'
REST_ADRESSE = 'http://192.168.1.101:3001/'

DIRECTORY_WEB_LOG = '.'
DIRECTORY_DOWNLOAD_DESTINATION_TEMP = '/mnt/HD/HD_a2/telechargement/temp_plowdown/'
DIRECTORY_DOWNLOAD_DESTINATION_ID = 1
DIRECTORY_DOWNLOAD_DESTINATION = '/mnt/HD/HD_a2/telechargement/'

# CONFIG_FILE = '/var/www/plow_solution/config.cfg'
CONFIG_FILE = '/var/www/plow_solution_test/config.cfg'

LOG_OUTPUT = True
CONSOLE_OUTPUT = True
LOG_BDD = False

DEFAULT_UNIREST_TIMEOUT = 30
FAST_UNIREST_TIMEOUT = 3

RESCUE_MODE = False


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


def find_element_by_attribute_in_object_array(array, attribute_to_find, value_to_find):
    returned = None

    for x in array:
        if getattr(x, attribute_to_find) == value_to_find:
            returned = x
            break

    return returned


def change_element_by_attribute_in_object_array(array, attribute_to_find, value_to_find, attribute_to_change, value_to_change):
    found = False

    for x in array:
        if getattr(x, attribute_to_find) == value_to_find:
            setattr(x, attribute_to_change, value_to_change)
            found = True
            break

    return found


def change_action_property(action, attribute_to_find, value_to_find, attribute_to_change, value_to_change):
    found = change_element_by_attribute_in_object_array(action.properties, attribute_to_find, value_to_find, attribute_to_change, value_to_change)
    if found is False:
        prop = Property()
        prop.action_id = action.id
        prop.property_id = value_to_find
        prop.property_value = value_to_change
        action.properties.append(prop)


def json_to_application_configuration_object(json_object):
    if bool(json_object):
        application_configuration = ApplicationConfiguration()
        application_configuration.id = json_object['id']
        application_configuration.download_activated = json_object['download_activated']
        application_configuration.log_debug_activated = json_object['log_debug_activated']

        return application_configuration
    else:
        return None


def json_to_application_configuration_list(json_array):
    list_application_configuration = []

    for json_object in json_array:
        application_configuration = json_to_application_configuration_object(json_object)
        list_application_configuration.append(application_configuration)

    return list_application_configuration


def json_to_download_object(json_object):
    if bool(json_object) is not False:
        download = Download()
        download.id = json_object['id']
        download.name = json_object['name']
        if json_object['host_id']:
            host = json_to_download_host_object(json_object['download_host'])
        else:
            host = None
        download.host = host
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
    else:
        return None


def json_to_download_object_list(json_array):
    list_downloads = []

    for json_object in json_array:
        download = json_to_download_object(json_object)
        list_downloads.append(download)

    return list_downloads


def json_to_download_package_object(json_object):
    if bool(json_object) is not False:
        download_package = DownloadPackage()
        download_package.id = json_object['id']
        download_package.name = json_object['name']
        download_package.unrar_percent = json_object['unrar_progress']

        return download_package
    else:
        return None


def json_to_download_directory_object(json_object):
    if bool(json_object) is not False:
        download_directory = DownloadDirectory()
        download_directory.id = json_object['id']
        download_directory.path = json_object['path']

        return download_directory
    else:
        return None


def json_to_property_object(json_object):
    if bool(json_object) is not False:
        property_ = Property()
        property_.action_id = json_object['action_id']
        property_.property_id = json_object['property_id']
        property_.property_value = json_object['property_value']
        if json_object['directory_id']:
            property_.directory = json_to_download_directory_object(json_object['directory'])
        else:
            property_.directory = None

        return property_
    else:
        return None


def json_to_property_object_list(json_array):
    list_properties = []

    for json_object in json_array:
        property_ = json_to_property_object(json_object)
        list_properties.append(property_)

    return list_properties


def json_to_action_object_list(json_array):
    list_actions = []

    for json_object in json_array:
        action = json_to_action_object(json_object)
        list_actions.append(action)

    return list_actions


def json_to_action_object(json_object):
    if bool(json_object) is not False:
        action = Action()
        action.id = json_object['id']
        action.lifecycle_insert_date = json_object['lifecycle_insert_date']
        action.lifecycle_update_date = json_object['lifecycle_update_date']
        action.download_id = json_object['download_id']
        action.download_package_id = json_object['download_package_id']
        action.action_status_id = json_object['action_status_id']
        action.action_type_id = json_object['action_type_id']
        action.properties = json_to_property_object_list(json_object['action_has_properties'])

        return action
    else:
        return None


def action_object_to_update_json(action_object):
    tab_properties = []

    for prop in action_object.properties:
        tab_properties.append({
            "action_id": prop.action_id,
            "property_id": prop.property_id,
            "property_value": prop.property_value,
            "directory_id": prop.directory.id if prop.directory is not None else None
        })

    action = {
        "id": action_object.id,
        "download_id": action_object.download_id,
        "download_package_id": action_object.download_package_id,
        "lifecycle_insert_date": action_object.lifecycle_insert_date,
        "lifecycle_update_date": action_object.lifecycle_update_date,
        "action_status_id": action_object.action_status_id,
        "action_type_id": action_object.action_type_id,
        "action_has_properties": tab_properties
    }

    return {"action": json.dumps(action)}


def json_to_download_host_object(json_object):
    if bool(json_object) is not False:
        download_host = DownloadHost()
        download_host.id = json_object['id']
        download_host.name = json_object['name']

        return download_host
    else:
        return None


def package_name_from_download_name(download_name):
    ext = download_name.split(".")[-1]
    ext2 = download_name.split(".")[-2]
    log_debug('Extensions %s | %s ' % (ext, ext2))
    if ext == 'rar':
        if 'part' in ext2:
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


def copy_large_file(src, dst, action=None, status=None, properties_treatment=None):
    '''
    Copy a large file showing progress.
    '''
    print('copying "{}" --> "{}"'.format(src, dst))
    if os.path.exists(src) is False:
        print('ERROR: file does not exist: "{}"'.format(src))
        sys.exit(1)
    if os.path.exists(dst) is True:
        os.remove(dst)
    if os.path.exists(dst) is True:
        print('ERROR: file exists, cannot overwrite it: "{}"'.format(dst))
        sys.exit(1)

    # Start the timer and get the size.
    start = time.time()
    size = os.stat(src).st_size
    print('{} bytes'.format(size))

    # Adjust the chunk size to the input size.
    divisor = 10000  # .1%
    chunk_size = size / divisor
    while chunk_size == 0 and divisor > 0:
        divisor /= 10
        chunk_size = size / divisor
    print('chunk size is {}'.format(chunk_size))

    # Copy.
    try:
        with open(src, 'rb') as ifp:
            with open(dst, 'wb') as ofp:
                copied = 0  # bytes
                chunk = ifp.read(chunk_size)
                while chunk:
                    # Write and calculate how much has been written so far.
                    ofp.write(chunk)
                    copied += len(chunk)
                    per = 100. * float(copied) / float(size)

                    # Calculate the estimated time remaining.
                    elapsed = time.time() - start  # elapsed so far
                    avg_time_per_byte = elapsed / float(copied)
                    remaining = size - copied
                    est = remaining * avg_time_per_byte
                    est1 = size * avg_time_per_byte

                    if properties_treatment is None:
                        eststr = 'ela={:>.1f}s, rem={:>.1f}s, tot={:>.1f}s'.format(elapsed, est, est1)

                        # Write out the status.
                        sys.stdout.write('\r\033[K{:>6.1f}%  {}  {} --> {} '.format(per, eststr, src, dst))
                        sys.stdout.flush()
                    else:
                        eststr = 'ela={:>.1f}s, rem={:>.1f}s, tot={:>.1f}s'.format(elapsed, est, est1)
                        log_debug('\r\033[K{:>6.1f}%  {}  {} --> {} '.format(per, eststr, src, dst))

                        properties_treatment(action, status, per, est, elapsed)

                    # Read in the next chunk.
                    chunk = ifp.read(chunk_size)

                # on verifie qu'on a copie tous les octets et qu'on a bien le fichier en destination
                if copied == size and os.path.isfile(dst):
                    os.remove(src)

    except IOError as obj:
        print('\nERROR: {}'.format(obj))
        sys.exit(1)

    sys.stdout.write('\r\033[K')  # clear to EOL
    elapsed = time.time() - start
    print('copied "{}" --> "{}" in {:>.1f}s"'.format(src, dst, elapsed))