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
import inspect
import time

from treatment import Treatment
from bean.actionBean import Action
from service.applicationConfigurationResource import ApplicationConfigurationResource
from service.downloadResource import DownloadResource
from downloads_main_manager import DownloadsMainManager

COMMAND_USAGE = 'usage: script start|stop (download_id)'


def main(argv):
    logging.getLogger("requests").setLevel(logging.WARNING)

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
        config.init()
        config_object = {}
        print("lookup for file config: " + config.CONFIG_FILE)
        if os.path.isfile(config.CONFIG_FILE):
            print("config file found " + config.CONFIG_FILE)
            exec(open(config.CONFIG_FILE, encoding='utf-8').read(), config_object)
            print(config_object['PYTHON_LOG_DIRECTORY'])
            config.application_configuration.id_application = config_object['PYTHON_APPLICATION_ID']
            config.application_configuration.python_log_directory.path = config_object['PYTHON_LOG_DIRECTORY']

            log.init('application.log')
            # log.init_log_file('application.log', config.application_configuration.python_log_format)
            # on initialise le log console par defaut
            # log.init_log_console(config.application_configuration.python_log_format)

            log.log(__name__, sys._getframe().f_code.co_name, "Config file found => %s" % config.CONFIG_FILE, log.LEVEL_INFO)

            config.application_configuration.rest_address = config_object['REST_ADRESS']
        else:
            log.log(__name__, sys._getframe().f_code.co_name, "No config file found, use default parameters", log.LEVEL_ALERT)

        # get the settings from the database
        try:
            config.application_configuration = ApplicationConfigurationResource.get(config.application_configuration.id_application)

            # if the settings is not found in database use the local config file
            if config.application_configuration is None:
                log.log(__name__, sys._getframe().f_code.co_name, "No configuration found in database, use locale config file", log.LEVEL_ERROR)
                utils.config_from_file(config_object)
        except:
            import traceback

            print(traceback.format_exc().splitlines()[-1])
            print("Traceback: %s" % traceback.format_exc())

            # no connection use the local config file
            utils.config_from_file(config_object)

            log.log(__name__, sys._getframe().f_code.co_name, "Error database connection, use local config file", log.LEVEL_ERROR)

        log.log(__name__, sys._getframe().f_code.co_name, "", log.LEVEL_DEBUG)
        log.log(__name__, sys._getframe().f_code.co_name, "************** Configuration informations **************", log.LEVEL_DEBUG)
        log.log(__name__, sys._getframe().f_code.co_name, "***** PYTHON_APPLICATION_ID: %d" % config.application_configuration.id_application, log.LEVEL_DEBUG)
        log.log(__name__, sys._getframe().f_code.co_name, "***** REST_ADDRESS: %s" % config.application_configuration.rest_address, log.LEVEL_DEBUG)
        log.log(__name__, sys._getframe().f_code.co_name, "***** NOTIFICATION_ADDRESS: %s" % config.application_configuration.notification_address, log.LEVEL_DEBUG)
        log.log(__name__, sys._getframe().f_code.co_name, "***** PYTHON_LOG_FORMAT: %s" % config.application_configuration.python_log_format, log.LEVEL_DEBUG)
        log.log(__name__, sys._getframe().f_code.co_name, "***** PYTHON_LOG_DIRECTORY: %s" % config.application_configuration.python_log_directory.to_string(), log.LEVEL_DEBUG)
        log.log(__name__, sys._getframe().f_code.co_name, "***** PYTHON_DIRECTORY_DOWNLOAD_TEMP: %s" % config.application_configuration.python_directory_download_temp.to_string(), log.LEVEL_DEBUG)
        log.log(__name__, sys._getframe().f_code.co_name, "***** PYTHON_DIRECTORY_DOWNLOAD: %s" % config.application_configuration.python_directory_download.to_string(), log.LEVEL_DEBUG)
        log.log(__name__, sys._getframe().f_code.co_name, "***** PYTHON_DIRECTORY_DOWNLOAD_TEXT: %s" % config.application_configuration.python_directory_download_text.to_string(), log.LEVEL_DEBUG)
        log.log(__name__, sys._getframe().f_code.co_name, "***** PYTHON_PERIODIC_CHECK_MINUTES: %d" % config.application_configuration.periodic_check_minutes, log.LEVEL_DEBUG)
        log.log(__name__, sys._getframe().f_code.co_name, "***** RESCUE_MODE: %s" % config.RESCUE_MODE, log.LEVEL_DEBUG)
        log.log(__name__, sys._getframe().f_code.co_name, "********************************************************", log.LEVEL_DEBUG)
        log.log(__name__, sys._getframe().f_code.co_name, "", log.LEVEL_DEBUG)

        treatment = Treatment()
        if args[0] == 'normal':
            log.init('normal')
            log.log(__name__, sys._getframe().f_code.co_name, "*** Start application ***", log.LEVEL_INFO)

            downloads_main_manger = DownloadsMainManager()
            downloads_main_manger.start()

            log.log(__name__, sys._getframe().f_code.co_name, "*** Stop application ***", log.LEVEL_INFO)

        # start a download
        elif args[0] == 'start':
            logging.basicConfig(filename=config.application_configuration.python_log_directory.path + 'log_start.log', level=config.application_configuration.python_log_level,
                                format='%(asctime)s %(message)s',
                                datefmt='%d/%m/%Y %H:%M:%S')
            log.log(__name__, sys._getframe().f_code.co_name, "*** Start application ***", log.LEVEL_INFO)

            if len(args) > 1:
                download_id = int(args[1])
                treatment.start_download(download_id)
            else:
                print(COMMAND_USAGE)
        # stop a download
        elif args[0] == 'stop':
            logging.basicConfig(filename=config.application_configuration.python_log_directory.path + 'log_stop.log', level=config.application_configuration.python_log_level,
                                format='%(asctime)s %(message)s',
                                datefmt='%d/%m/%Y %H:%M:%S')
            log.log(__name__, sys._getframe().f_code.co_name, "*** Start application ***", log.LEVEL_INFO)
            if len(args) > 1:
                download_id = int(args[1])
                treatment.stop_download(download_id)
            else:
                print(COMMAND_USAGE)
        elif args[0] == 'start_file_treatment':
            if len(args) > 1:
                file_path = args[1]
                treatment.start_file_treatment(file_path)
            else:
                print(COMMAND_USAGE)
        elif args[0] == 'start_multi_downloads':
            if len(args) > 1:
                file_path = args[1]
                treatment.start_multi_downloads(file_path)
        elif args[0] == 'stop_multi_downloads':
            logging.basicConfig(filename=config.application_configuration.python_log_directory.path + 'log_stop_multi_downloads.log', level=config.application_configuration.python_log_level,
                                format='%(asctime)s %(message)s',
                                datefmt='%d/%m/%Y %H:%M:%S')
            log.log(__name__, sys._getframe().f_code.co_name, "*** Start application ***", log.LEVEL_INFO)
            if len(args) > 1:
                file_path = args[1]
                treatment.stop_multi_downloads(file_path)
        elif args[0] == 'stop_current_downloads':
            logging.basicConfig(filename=config.application_configuration.python_log_directory.path + 'log_stop_current_downloads.log', level=config.application_configuration.python_log_level,
                                format='%(asctime)s %(message)s',
                                datefmt='%d/%m/%Y %H:%M:%S')
            log.log(__name__, sys._getframe().f_code.co_name, "*** Start application ***", log.LEVEL_INFO)
            treatment.stop_current_downloads()
        elif args[0] == 'check_download_alive':
            logging.basicConfig(filename=config.application_configuration.python_log_directory.path + 'log_check_download_alive.log', level=config.application_configuration.python_log_level,
                                format='%(asctime)s %(message)s',
                                datefmt='%d/%m/%Y %H:%M:%S')
            log.log(__name__, sys._getframe().f_code.co_name, "*** Start application ***", log.LEVEL_INFO)
            if len(args) > 1:
                download_id = int(args[1])
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

                    logging.basicConfig(filename=config.application_configuration.python_log_directory.path + file_name, level=config.application_configuration.python_log_level,
                                        format='%(asctime)s %(message)s',
                                        datefmt='%d/%m/%Y %H:%M:%S')
                    treatment.action(o['object_id'], o['action_id'], o['action_target_id'])
            else:
                print(COMMAND_USAGE)
        elif args[0] == 'unrar':
            logging.basicConfig(filename=config.application_configuration.python_log_directory.path + 'unrar.log', level=config.application_configuration.python_log_level,
                                format='%(asctime)s %(message)s',
                                datefmt='%d/%m/%Y %H:%M:%S')
            if len(args) > 1:
                download_id = int(args[1])
                treatment.unrar(download_id)
            else:
                print(COMMAND_USAGE)
        elif args[0] == 'reset':
            logging.basicConfig(filename=config.application_configuration.python_log_directory.path + 'reset.log', level=config.application_configuration.python_log_level,
                                format='%(asctime)s %(message)s',
                                datefmt='%d/%m/%Y %H:%M:%S')
            if len(args) > 2:
                download_id = int(args[1])
                file_to_delete = (args[2] == "true")
                treatment.reset(download_id, file_to_delete)
            else:
                print(COMMAND_USAGE)
        elif args[0] == 'delete_package_files':
            logging.basicConfig(filename=config.application_configuration.python_log_directory.path + 'delete_package_files.log', level=config.application_configuration.python_log_level,
                                format='%(asctime)s %(message)s',
                                datefmt='%d/%m/%Y %H:%M:%S')
            if len(args) > 1:
                package_id = int(args[1])
                treatment.delete_package_files(package_id)
            else:
                print(COMMAND_USAGE)
        elif args[0] == 'update_plowshare':
            treatment.update_plowshare()
        elif args[0] == 'test':
            if len(args) > 1:
                fct_to_test_name = args[1]
                print(args[2])
                getattr(Treatment, fct_to_test_name)(args[2])
        else:
            print(COMMAND_USAGE)


if __name__ == "__main__":
    main(sys.argv[1:])
