__author__ = 'vcapi'

import log
import config
import requests
import utils
from datetime import datetime, timedelta
from bean.downloadBean import Download


class HostResource(object):
    @staticmethod
    def insert(host_to_insert):
        log.log('[HostResource](Insert) +++', log.LEVEL_INFO)

        host_inserted = None
        if host_to_insert is not None:
            try:
                log.log(
                    '[HostResource](Insert) | ' + config.REST_ADRESSE + 'downloadHosts \r\n params: %s' % host_to_insert.to_insert_json(), log.LEVEL_DEBUG)

                response = requests.post(config.REST_ADRESSE + 'downloadHosts',
                                        data=host_to_insert.to_insert_json())

                if response.status_code != 200:
                    log.log('[HostResource](Insert) | Error insert host %s => %s' % (response.status_code, response.json()), log.LEVEL_ERROR)
                    raise Exception('[HostResource](Insert) | Error insert host %s => %s' % (response.status_code, response.json()))
                else:
                    host_inserted = utils.json_to_download_host_object(response.json())

            except Exception:
                import traceback
                log.log("[HostResource](Insert) | Insert host: No database connection \r\n %s" % traceback.format_exc().splitlines()[-1], log.LEVEL_ERROR)
                log.log("[HostResource](Insert) | Traceback: %s" % traceback.format_exc(), log.LEVEL_DEBUG)

        else:
            log.log("[HostResource](Insert) | Host is none", log.LEVEL_ERROR)

        return host_inserted