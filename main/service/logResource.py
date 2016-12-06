__author__ = 'vcapi'

import log
import config
import requests
import utils
import json
import sys
from datetime import datetime, timedelta
from bean.downloadBean import Download


class LogResource(object):
    @staticmethod
    def insert(download_id, logs, application_configuration_id, to_insert_in_database=False):
        log_inserted = None

        try:
            params = {"logs": json.dumps({"id": download_id, "logs": logs}), "applicationConfigurationId": application_configuration_id, "insert": 'true' if to_insert_in_database is True else 'false'}
            # log.log(__name__, sys._getframe().f_code.co_name, config.application_configuration.rest_address + 'downloads/logs/%d => params: %s' % (download_id, params), log.LEVEL_DEBUG)
            response = requests.put(config.application_configuration.rest_address + 'downloads/logs/%d' % download_id,
                                    data=params)

            if response.status_code != 200:
                log.log(__name__, sys._getframe().f_code.co_name, 'Error insert log %s => %s' % (
                    response.status_code, response.json()), log.LEVEL_ERROR)
                raise Exception('Error insert package %s => %s' % (
                    response.status_code, response.json()))
            
        except Exception:
            import traceback

            log.log(__name__, sys._getframe().f_code.co_name, "Insert package: No database connection => %s" %
                    traceback.format_exc().splitlines()[-1], log.LEVEL_ERROR)
            log.log(__name__, sys._getframe().f_code.co_name, "Traceback: %s" % traceback.format_exc(), log.LEVEL_DEBUG)

        return log_inserted
