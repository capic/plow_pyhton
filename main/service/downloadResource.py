__author__ = 'vcapi'

import log
import config
import requests
import utils
from datetime import datetime, timedelta
from bean.downloadBean import Download


class DownloadResource(object):
    @staticmethod
    def get(download_id):
        log.log('[DownloadResource](get) +++', log.LEVEL_INFO)

        download = None
        if download_id is not None:
            try:
                log.log('[DownloadResource](get) | ' + config.REST_ADRESSE + 'downloads/%d' % download_id,
                        log.LEVEL_DEBUG)
                response = requests.get(config.REST_ADRESSE + 'downloads/%d' % download_id)

                if response.status_code == 200:
                    log.log('[DownloadResource](get) | download got: %s' % response.json(), log.LEVEL_DEBUG)
                    download = utils.json_to_download_object(response.json())
                else:
                    log.log('[DownloadResource](get) | Error get %s => %s' % (response.code, response.json()),
                            log.LEVEL_ERROR)
            except Exception:
                import traceback

                log.log("[DownloadResource](get) | Get download by id: No database connection \r\n %s" %
                        traceback.format_exc().splitlines()[-1],
                        log.LEVEL_ERROR)
                log.log("[DownloadResource](get) | Traceback: %s" % traceback.format_exc(), log.LEVEL_DEBUG)
        else:
            log.log('[DownloadResource](get) | Id is none', log.LEVEL_ERROR)

        return download

    @staticmethod
    def get_next(params):
        log.log('[DownloadResource](get) +++', log.LEVEL_INFO)

        download = None
        try:
            if params is None:
                log.log('[DownloadResource](get_next) | ' + config.REST_ADRESSE + 'downloads/next', log.LEVEL_DEBUG)
                response = requests.get(config.REST_ADRESSE + 'downloads/next')
            else:
                log.log('[DownloadResource](get_next) | ' + config.REST_ADRESSE + 'downloads/next \r\n params: %s' % params, log.LEVEL_DEBUG)
                response = requests.get(config.REST_ADRESSE + 'downloads/next', params=params)

            if response.status_code == 200:
                log.log('[DownloadResource](get_next) | download got: %s' % response.json(), log.LEVEL_DEBUG)
                download = utils.json_to_download_object(response.json())
            else:
                log.log('[DownloadResource](get_next) | Error get %s => %s' % (response.code, response.json()),
                        log.LEVEL_ERROR)
        except Exception:
            import traceback

            log.log("[DownloadResource](get_next) | Get next download: No database connection \r\n %s" %
                    traceback.format_exc().splitlines()[-1],
                    log.LEVEL_ERROR)
            log.log("[DownloadResource](get_next) | Traceback: %s" % traceback.format_exc(), log.LEVEL_DEBUG)
        else:
            log.log('[DownloadResource](get) | Id is none', log.LEVEL_ERROR)

        return download

    @staticmethod
    def get_all_by_params(params):
        log.log('[DownloadResource](get_all_by_params) +++', log.LEVEL_INFO)

        downloads_list = None
        if params is not None:
            try:
                log.log(
                    '[DownloadResource](get_all_by_params) | ' + config.REST_ADRESSE + 'downloads \r\n params: %s' % params,
                    log.LEVEL_DEBUG)
                response = requests.get(config.REST_ADRESSE + 'downloads',
                                        params=params)

                if response.status_code == 200:
                    downloads_list = utils.json_to_download_object_list(response.json())
                else:
                    log.log(
                        '[DownloadResource](get_all_by_params) | Error get %s => %s' % (response.code, response.json()),
                        log.LEVEL_ERROR)
            except Exception:
                import traceback

                log.log(
                    "[DownloadResource](get_all_by_params) | Get all actions by params: No database connection \r\n %s" %
                    traceback.format_exc().splitlines()[-1],
                    log.LEVEL_ERROR)
                log.log("[DownloadResource](get_all_by_params) | Traceback: %s" % traceback.format_exc(),
                        log.LEVEL_DEBUG)
        else:
            log.log('[DownloadResource](get_all_by_params) | Params is none', log.LEVEL_ERROR)

        return downloads_list

    @staticmethod
    def insert(download_to_insert):
        log.log('[DownloadResource](Insert) +++', log.LEVEL_INFO)

        log.log(
            '[DownloadResource](Insert) |' + config.REST_ADRESSE + 'downloads \r\n params: %s' % download_to_insert.to_insert_json(),
            log.LEVEL_DEBUG)

        response = requests.post(config.REST_ADRESSE + 'downloads', data=download_to_insert.to_insert_json())

        if response.status_code != 200:
            log.log('[DownloadResource](Insert) | Error insert %s => %s' % (response.code, response.json()),
                    log.LEVEL_ERROR)
            raise Exception(
                '[DownloadResource](Insert) | Error insert %s => %s' % (response.status_code, response.json()))
        else:
            return DownloadResource.get(response.json()['id'])

    @staticmethod
    def update(download_to_update):
        log.log('[DownloadResource](update) +++', log.LEVEL_INFO)

        download_to_update.lifecycle_update_date = datetime.utcnow().isoformat()

        try:
            download_updated = None

            log.log('[DownloadResource](update) | ' + config.REST_ADRESSE + 'downloads/%d \r\n %s' % (
                download_to_update.id, download_to_update.to_update_object()), log.LEVEL_DEBUG)

            response = requests.put(config.REST_ADRESSE + 'downloads/%d' % download_to_update.id,
                                    data=download_to_update.to_update_object())

            if response.code != 200:
                log.log('[DownloadResource](update) | Error update %s => %s' % (response.code, response.json()),
                        log.LEVEL_ERROR)
                download_to_update.logs = "ERROR DURING DOWNLOAD UPDATE\r\n"
            else:
                download_updated = utils.json_to_download_object(response.json())

            return download_updated

        except Exception:
            import traceback

            log.log("[DownloadResource](update) | Update download: No database connection \r\n %s" %
                    traceback.format_exc().splitlines()[-1],
                    log.LEVEL_ERROR)
            log.log("[DownloadResource](update) | Traceback: %s" % traceback.format_exc(), log.LEVEL_DEBUG)
            raise
