# coding: utf8
# !/usr/bin/env python

__author__ = 'Vincent'

import sys
import getopt
import logging
import utils

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
        treatment = Treatment()

        # start a download
        if args[0] == 'start':
            logging.basicConfig(filename='/var/www/log/log_start.log', level=logging.DEBUG,
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
            logging.basicConfig(filename='/var/www/log/log_stop.log', level=logging.DEBUG,
                                format='%(asctime)s %(message)s',
                                datefmt='%d/%m/%Y %H:%M:%S')
            utils.log_debug(u"*** Start application ***")
            if len(args) > 1:
                download_id = args[1]
                treatment.stop_download(download_id)
            else:
                print(COMMAND_USAGE)
        elif args[0] == 'start_file_treatment':
            logging.basicConfig(filename='/var/www/log/log_start_file_treatment.log', level=logging.DEBUG,
                                format='%(asctime)s %(message)s',
                                datefmt='%d/%m/%Y %H:%M:%S')
            utils.log_debug(u"*** Start application ***")
            if len(args) > 1:
                file_path = args[1]
                treatment.start_file_treatment(file_path)
            else:
                print(COMMAND_USAGE)
        elif args[0] == 'start_multi_downloads':
            logging.basicConfig(filename='/var/www/log/log_start_multi_downloads.log', level=logging.DEBUG,
                                format='%(asctime)s %(message)s',
                                datefmt='%d/%m/%Y %H:%M:%S')
            utils.log_debug(u"*** Start application ***")
            if len(args) > 1:
                file_path = args[1]
                treatment.start_multi_downloads(file_path)
        elif args[0] == 'stop_multi_downloads':
            logging.basicConfig(filename='/var/www/log/log_stop_multi_downloads.log', level=logging.DEBUG,
                                format='%(asctime)s %(message)s',
                                datefmt='%d/%m/%Y %H:%M:%S')
            utils.log_debug(u"*** Start application ***")
            if len(args) > 1:
                file_path = args[1]
                treatment.stop_multi_downloads(file_path)
        elif args[0] == 'check_download_alive':
            logging.basicConfig(filename='/var/www/log/log_check_download_alive.log', level=logging.DEBUG,
                                format='%(asctime)s %(message)s',
                                datefmt='%d/%m/%Y %H:%M:%S')
            utils.log_debug(u"*** Start application ***")
            if len(args) > 1:
                download_id = args[1]
                treatment.check_download_alive(download_id)
            else:
                treatment.check_multi_downloads_alive()
        else:
            print(COMMAND_USAGE)

        treatment.disconnect()


if __name__ == "__main__":
    main(sys.argv[1:])
