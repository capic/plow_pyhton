__author__ = 'vcapi'

import log
import config
import requests
import utils
from datetime import datetime, timedelta
from bean.downloadBean import Download


class LogResource(object):
    @staticmethod
    def insert(download_log_to_insert):
        log.log('[LogResource](insert) +++', log.LEVEL_INFO)

        log_inserted = None
        if download_log_to_insert is not None:
            try:
                params = {"id": download_log_to_insert.id, "logs": download_log_to_insert.logs}
                log.log('[LogResource](insert_log) | ' + config.REST_ADRESSE + 'downloads/logs/%d \r\n params: %s' % (
                    download_log_to_insert.id, params), log.LEVEL_DEBUG)
                response = requests.put(config.REST_ADRESSE + 'downloads/logs/%d' % download_log_to_insert.id,
                                        data=params)

                if response.status_code != 200:
                    log.log('[LogResource](insert_log) | Error insert log %s => %s' % (
                        response.status_code, response.json()), log.LEVEL_ERROR)
                    raise Exception('[LogResource](insert_log) | Error insert package %s => %s' % (
                        response.status_code, response.json()))
                else:
                    log_inserted = response.json()['logs']

            except Exception:
                import traceback

                log.log("[DownloadResource](Insert) | Insert package: No database connection \r\n %s" %
                        traceback.format_exc().splitlines()[-1], log.LEVEL_ERROR)
                log.log("[DownloadResource](Insert) | Traceback: %s" % traceback.format_exc(), log.LEVEL_DEBUG)

        else:
            log.log("[DownloadResource](Insert) | Download log is none", log.LEVEL_ERROR)

        return log_inserted