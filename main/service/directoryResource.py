__author__ = 'vcapi'

import log
import config
import requests
import utils
import sys
from datetime import datetime, timedelta
from bean.downloadBean import Download


class DirectoryResource(object):
    @staticmethod
    def get(directory_id):
        directory = None
        if directory_id is not None:
            try:
                log.log(__name__, sys._getframe().f_code.co_name, config.application_configuration.rest_address + 'downloadDirectories/%d' + directory_id, log.LEVEL_DEBUG)
                response = requests.get(config.application_configuration.rest_address + 'downloadDirectories/%d' + directory_id)

                if response.status_code == 200:
                    log.log(__name__, sys._getframe().f_code.co_name, 'package got: %s' % response.json(), log.LEVEL_DEBUG)
                    directory = utils.json_to_download_directory_object(response.json())
                else:
                    log.log(__name__, sys._getframe().f_code.co_name, 'Error get %s => %s' % (response.status_code, response.json()),
                            log.LEVEL_ERROR)
            except Exception:
                import traceback

                log.log(__name__, sys._getframe().f_code.co_name, "Get directory by id: No database connection => %s" %
                        traceback.format_exc().splitlines()[-1],
                        log.LEVEL_ERROR)
                log.log(__name__, sys._getframe().f_code.co_name, "Traceback: %s" % traceback.format_exc(), log.LEVEL_DEBUG)
        else:
            log.log(__name__, sys._getframe().f_code.co_name, 'Id is none', log.LEVEL_ERROR)

        return directory