
# !/usr/bin/env python

__author__ = 'Vincent'

import sys
import getopt
import logging
import utils
import os
import json
import log
import config
from inspect import signature

from treatment import Treatment
from bean.actionBean import Action

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
        if os.path.isfile(config.CONFIG_FILE):
            config_object = {}
            exec(open(config.CONFIG_FILE, encoding='utf-8').read(), config_object)

            if 'rest_adresse' in config_object:
                config.REST_ADRESSE = config_object['rest_adresse']
            if 'repertoire_web_log' in config_object:
                config.DIRECTORY_WEB_LOG = config_object['repertoire_web_log']
            if 'repertoire_telechargement_temporaire' in config_object:
                config.DIRECTORY_DOWNLOAD_DESTINATION_TEMP = config_object['repertoire_telechargement_temporaire']
            if 'repertoire_telechargement_id' in config_object:
                config.DIRECTORY_DOWNLOAD_DESTINATION_ID = config_object['repertoire_telechargement_id']
            if 'repertoire_telechargement' in config_object:
                config.DIRECTORY_DOWNLOAD_DESTINATION = config_object['repertoire_telechargement']
            if 'log_output' in config_object:
                config.LOG_OUTPUT = (
                    config_object['log_output'] == "True" or config_object['log_output'] == "true" or config_object['log_output'] == "1")
            if 'console_output' in config_object:
                config.CONSOLE_OUTPUT = (
                    config_object['console_output'] == "True" or config_object['console_output'] == "true" or config_object[
                        'console_output'] == "1")
            if 'log_bdd' in config_object:
                config.LOG_BDD = (
                    config_object['log_bdd'] == "True" or config_object['log_bdd'] == "true" or config_object[
                        'log_bdd'] == "1")
            if 'log_level' in config_object:
                config.CONFIG_LOG_LEVEL = config_object['log_level']
                log.convert_log_level_to_logging_level()

        log.log("Rest Address: %s" % config.REST_ADRESSE, log.LEVEL_DEBUG)
        log.log("Directory web log %s" % config.DIRECTORY_WEB_LOG, log.LEVEL_DEBUG)
        log.log("Directory download destination temp %s" % config.DIRECTORY_DOWNLOAD_DESTINATION_TEMP, log.LEVEL_DEBUG)
        log.log("Directory download destination %s" % config.DIRECTORY_DOWNLOAD_DESTINATION, log.LEVEL_DEBUG)
        log.log("Log output %s" % str(config.LOG_OUTPUT), log.LEVEL_DEBUG)
        log.log("Console output %s" % str(config.CONSOLE_OUTPUT), log.LEVEL_DEBUG)

        treatment = Treatment()

        # start a download
        if args[0] == 'start':
            logging.basicConfig(filename=config.DIRECTORY_WEB_LOG + 'log_start.log', level=config.CONFIG_LOG_LEVEL_LOGGING,
                                format='%(asctime)s %(message)s',
                                datefmt='%d/%m/%Y %H:%M:%S')
            log.log("*** Start application ***", log.LEVEL_INFO)

            if len(args) > 1:
                download_id = args[1]
                treatment.start_download(download_id)
            else:
                print(COMMAND_USAGE)
        # stop a download
        elif args[0] == 'stop':
            logging.basicConfig(filename=config.DIRECTORY_WEB_LOG + 'log_stop.log', level=config.CONFIG_LOG_LEVEL_LOGGING,
                                format='%(asctime)s %(message)s',
                                datefmt='%d/%m/%Y %H:%M:%S')
            log.log("*** Start application ***", log.LEVEL_INFO)
            if len(args) > 1:
                download_id = args[1]
                treatment.stop_download(download_id)
            else:
                print(COMMAND_USAGE)
        elif args[0] == 'start_file_treatment':
            logging.basicConfig(filename=config.DIRECTORY_WEB_LOG + 'log_start_file_treatment.log', level=config.CONFIG_LOG_LEVEL_LOGGING,
                                format='%(asctime)s %(message)s',
                                datefmt='%d/%m/%Y %H:%M:%S')
            log.log("*** Start application ***", log.LEVEL_INFO)
            if len(args) > 1:
                file_path = args[1]
                treatment.start_file_treatment(file_path)
            else:
                print(COMMAND_USAGE)
        elif args[0] == 'start_multi_downloads':
            # logging.basicConfig(filename=config.DIRECTORY_WEB_LOG +'log_start_multi_downloads.log', level=config.CONFIG_LOG_LEVEL_LOGGING,
            # format='%(asctime)s %(message)s',
            # datefmt='%d/%m/%Y %H:%M:%S')
            # log.log_debug("*** Start application ***")
            if len(args) > 1:
                file_path = args[1]
                treatment.start_multi_downloads(file_path)
        elif args[0] == 'stop_multi_downloads':
            logging.basicConfig(filename=config.DIRECTORY_WEB_LOG + 'log_stop_multi_downloads.log', level=config.CONFIG_LOG_LEVEL_LOGGING,
                                format='%(asctime)s %(message)s',
                                datefmt='%d/%m/%Y %H:%M:%S')
            log.log("*** Start application ***", log.LEVEL_INFO)
            if len(args) > 1:
                file_path = args[1]
                treatment.stop_multi_downloads(file_path)
        elif args[0] == 'check_download_alive':
            logging.basicConfig(filename=config.DIRECTORY_WEB_LOG + 'log_check_download_alive.log', level=config.CONFIG_LOG_LEVEL_LOGGING,
                                format='%(asctime)s %(message)s',
                                datefmt='%d/%m/%Y %H:%M:%S')
            log.log("*** Start application ***", log.LEVEL_INFO)
            if len(args) > 1:
                download_id = args[1]
                treatment.check_download_alive(download_id)
            else:
                treatment.check_multi_downloads_alive()
        elif args[0] == 'action':
            if len(args) > 1:
                tab = json.loads(args[1])
                for o in tab:
                    file_name = 'action_' + str(o['action_id'])
                    if o['action_target_id'] == Action.TARGET_DOWNLOAD:
                        file_name += 'download_'
                    elif o['action_target_id'] == Action.TARGET_PACKAGE:
                        file_name += 'package_'
                    file_name += str(o['object_id']) + '.log'

                    logging.basicConfig(filename=config.DIRECTORY_WEB_LOG + file_name, level=config.CONFIG_LOG_LEVEL_LOGGING,
                                        format='%(asctime)s %(message)s',
                                        datefmt='%d/%m/%Y %H:%M:%S')
                    treatment.action(o['object_id'], o['action_id'], o['action_target_id'])
            else:
                print(COMMAND_USAGE)
        elif args[0] == 'unrar':
            logging.basicConfig(filename=config.DIRECTORY_WEB_LOG + 'unrar.log', level=config.CONFIG_LOG_LEVEL_LOGGING,
                                format='%(asctime)s %(message)s',
                                datefmt='%d/%m/%Y %H:%M:%S')
            if len(args) > 1:
                download_id = args[1]
                treatment.unrar(download_id)
            else:
                print(COMMAND_USAGE)
        elif args[0] == 'reset':
            logging.basicConfig(filename=config.DIRECTORY_WEB_LOG + 'reset.log', level=config.CONFIG_LOG_LEVEL_LOGGING,
                                format='%(asctime)s %(message)s',
                                datefmt='%d/%m/%Y %H:%M:%S')
            if len(args) > 2:
                download_id = args[1]
                file_to_delete = (args[2] == "true")
                treatment.reset(download_id, file_to_delete)
            else:
                print(COMMAND_USAGE)
        elif args[0] == 'delete_package_files':
            logging.basicConfig(filename=config.DIRECTORY_WEB_LOG + 'delete_package_files.log', level=config.CONFIG_LOG_LEVEL_LOGGING,
                                format='%(asctime)s %(message)s',
                                datefmt='%d/%m/%Y %H:%M:%S')
            if len(args) > 1:
                package_id = args[1]
                treatment.delete_package_files(package_id)
            else:
                print(COMMAND_USAGE)
        elif args[0] == 'test':
            if len(args) > 1:
                fct_to_test_name = args[1]
                fct_to_test = getattr(Treatment, fct_to_test_name)
                sig = signature(fct_to_test)
                print(str(sig))

        else:
            print(COMMAND_USAGE)


if __name__ == "__main__":
    main(sys.argv[1:])
