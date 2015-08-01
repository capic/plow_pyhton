#!/usr/bin/env python

__author__ = 'Vincent'

import sys
import getopt
import logging

from treatment import Treatment


COMMAND_USAGE = 'usage: script start|stop (download_id)'


def main(argv):
    logging.basicConfig(filename='/var/www/log.log', level=logging.DEBUG, format='%(asctime)s %(message)s',
                        datefmt='%d/%m/%Y %H:%M:%S')
    logging.debug('*** Start application ***')

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
            if len(args) > 1:
                download_id = args[1]
                treatment.start_download(download_id)
            else:
                print(COMMAND_USAGE)
        # stop a download
        elif args[0] == 'stop':
            if len(args) > 1:
                download_id = args[1]
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
            if len(args) > 1:
                file_path = args[1]
                treatment.stop_multi_downloads(file_path)
        elif args[0] == 'check_download_alive':
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
