# coding: utf8
# !/usr/bin/env python

__author__ = 'Vincent'

import sys
import getopt
import logging
import utils
import os

from treatment import Treatment

COMMAND_USAGE = 'usage: script start|stop (download_id)'


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "", [])
    except getopt.GetoptError:
        print(COMMAND_USAGE)
        exit()

    if len(args) == 0:
        print("Parameters are missing")
        print(COMMAND_USAGE)
        exit()
    else:
        if os.path.isfile("/var/www/plow_solution/config.cfg"):
            config = {}
            execfile("/var/www/plow_solution/config.cfg", config)
            utils.log_debug("config file found")
            if 'rest_adresse' in config:
                utils.REST_ADRESSE = config['rest_adresse']
            if 'mysql_login' in config:
                utils.MYSQL_LOGIN = config['mysql_login']
            if 'mysql_pass' in config:
                utils.MYSQL_PASS = config['mysql_pass']
            if 'mysql_host' in config:
                utils.MYSQL_HOST = config['mysql_host']
            if 'mysql_database' in config:
                utils.MYSQL_DATABASE = config['mysql_database']
            if 'repertoire_web_log' in config:
                utils.DIRECTORY_WEB_LOG = config['repertoire_web_log']
            if 'repertoire_telechargement_temporaire' in config:
                utils.DIRECTORY_DOWNLOAD_DESTINATION_TEMP = config['repertoire_telechargement_temporaire']
            if 'repertoire_telechargement' in config:
                utils.DIRECTORY_DOWNLOAD_DESTINATION = config['repertoire_telechargement']
            if 'log_output' in config:
                utils.LOG_OUTPUT = (
                    config['log_output'] == "True" or config['log_output'] == "true" or config['log_output'] == "1")
            if 'console_output' in config:
                utils.CONSOLE_OUTPUT = (
                    config['console_output'] == "True" or config['console_output'] == "true" or config[
                        'console_output'] == "1")

        utils.log_debug("Directory web log %s" % utils.DIRECTORY_WEB_LOG)
        utils.log_debug("Directory download destination temp %s" % utils.DIRECTORY_DOWNLOAD_DESTINATION_TEMP)
        utils.log_debug("Directory download destination %s" % utils.DIRECTORY_DOWNLOAD_DESTINATION)
        utils.log_debug("Log output %s" % str(utils.LOG_OUTPUT))
        utils.log_debug("Console output %s" % str(utils.CONSOLE_OUTPUT))

        treatment = Treatment()

        # start a download
        if args[0] == 'start':
            logging.basicConfig(filename=utils.DIRECTORY_WEB_LOG + 'log_start.log', level=logging.DEBUG,
                                format='%(asctime)s %(message)s',
                                datefmt='%d/%m/%Y %H:%M:%S')
            utils.log_debug(u"*** Start application ***")

            if len(args) > 1:
                download_id = args[1]
                treatment.start_download(download_id)
            else:
                print(COMMAND_USAGE)
        # stop a download
        elif args[0] == 'stop':
            logging.basicConfig(filename=utils.DIRECTORY_WEB_LOG + 'log_stop.log', level=logging.DEBUG,
                                format='%(asctime)s %(message)s',
                                datefmt='%d/%m/%Y %H:%M:%S')
            utils.log_debug(u"*** Start application ***")
            if len(args) > 1:
                download_id = args[1]
                treatment.stop_download(download_id)
            else:
                print(COMMAND_USAGE)
        elif args[0] == 'start_file_treatment':
            logging.basicConfig(filename=utils.DIRECTORY_WEB_LOG + 'log_start_file_treatment.log', level=logging.DEBUG,
                                format='%(asctime)s %(message)s',
                                datefmt='%d/%m/%Y %H:%M:%S')
            utils.log_debug(u"*** Start application ***")
            if len(args) > 1:
                file_path = args[1]
                treatment.start_file_treatment(file_path)
            else:
                print(COMMAND_USAGE)
        elif args[0] == 'start_multi_downloads':
            # logging.basicConfig(filename=utils.DIRECTORY_WEB_LOG +'log_start_multi_downloads.log', level=logging.DEBUG,
            # format='%(asctime)s %(message)s',
            # datefmt='%d/%m/%Y %H:%M:%S')
            # utils.log_debug(u"*** Start application ***")
            if len(args) > 1:
                file_path = args[1]
                treatment.start_multi_downloads(file_path)
        elif args[0] == 'stop_multi_downloads':
            logging.basicConfig(filename=utils.DIRECTORY_WEB_LOG + 'log_stop_multi_downloads.log', level=logging.DEBUG,
                                format='%(asctime)s %(message)s',
                                datefmt='%d/%m/%Y %H:%M:%S')
            utils.log_debug(u"*** Start application ***")
            if len(args) > 1:
                file_path = args[1]
                treatment.stop_multi_downloads(file_path)
        elif args[0] == 'check_download_alive':
            logging.basicConfig(filename=utils.DIRECTORY_WEB_LOG + 'log_check_download_alive.log', level=logging.DEBUG,
                                format='%(asctime)s %(message)s',
                                datefmt='%d/%m/%Y %H:%M:%S')
            utils.log_debug(u"*** Start application ***")
            if len(args) > 1:
                download_id = args[1]
                treatment.check_download_alive(download_id)
            else:
                treatment.check_multi_downloads_alive()
        elif args[0] == 'move':
            logging.basicConfig(filename=utils.DIRECTORY_WEB_LOG + 'move.log', level=logging.DEBUG,
                                format='%(asctime)s %(message)s',
                                datefmt='%d/%m/%Y %H:%M:%S')
            if len(args) > 2:
                download_id = args[1]
                dest_directory_id = args[2]
                treatment.move_file(download_id, dest_directory_id)
            else:
                print(COMMAND_USAGE)
        elif args[0] == 'unrar':
            logging.basicConfig(filename=utils.DIRECTORY_WEB_LOG + 'unrar.log', level=logging.DEBUG,
                                format='%(asctime)s %(message)s',
                                datefmt='%d/%m/%Y %H:%M:%S')
            if len(args) > 1:
                download_id = args[1]
                treatment.unrar(download_id)
            else:
                print(COMMAND_USAGE)
        elif args[0] == 'reset':
            logging.basicConfig(filename=utils.DIRECTORY_WEB_LOG + 'reset.log', level=logging.DEBUG,
                                format='%(asctime)s %(message)s',
                                datefmt='%d/%m/%Y %H:%M:%S')
            if len(args) > 2:
                download_id = args[1]
                file_to_delete = (args[2] == "true")
                treatment.reset(download_id, file_to_delete)
            else:
                print(COMMAND_USAGE)
        else:
            print(COMMAND_USAGE)

        treatment.disconnect()


if __name__ == "__main__":
    main(sys.argv[1:])
