__author__ = 'vcapi'

import log
import config
import requests
import utils
import sys
from datetime import datetime, timedelta
from bean.downloadBean import Download


class HostResource(object):
    @staticmethod
    def insert(host_to_insert):
        host_inserted = None
        if host_to_insert is not None:
            try:
                log.log(__name__, sys._getframe().f_code.co_name,
                    config.application_configuration.rest_address + 'downloadHosts => params: %s' % host_to_insert.to_insert_json(), log.LEVEL_DEBUG)

                response = requests.post(config.application_configuration.rest_address + 'downloadHosts',
                                        data=host_to_insert.to_insert_json())

                if response.status_code != 200:
                    log.log(__name__, sys._getframe().f_code.co_name, 'Error insert host %s => %s' % (response.status_code, response.json()), log.LEVEL_ERROR)
                    raise Exception('Error insert host %s => %s' % (response.status_code, response.json()))
                else:
                    host_inserted = utils.json_to_download_host_object(response.json())

            except Exception:
                import traceback
                log.log(__name__, sys._getframe().f_code.co_name, "Insert host: No database connection => %s" % traceback.format_exc().splitlines()[-1], log.LEVEL_ERROR)
                log.log(__name__, sys._getframe().f_code.co_name, "Traceback: %s" % traceback.format_exc(), log.LEVEL_DEBUG)

        else:
            log.log(__name__, sys._getframe().f_code.co_name, "Host is none", log.LEVEL_ERROR)

        return host_inserted