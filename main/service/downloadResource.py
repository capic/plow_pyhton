__author__ = 'vcapi'

import log
import config
import requests
import utils
import sys
from datetime import datetime, timedelta
from bean.downloadBean import Download


class DownloadResource(object):
    @staticmethod
    def get(download_id):
        download = None
        if download_id is not None:
            try:
                log.log(__name__, sys._getframe().f_code.co_name, config.application_configuration.rest_address + 'downloads/%d' % download_id,
                        log.LEVEL_DEBUG)
                response = requests.get(config.application_configuration.rest_address + 'downloads/%d' % download_id)

                if response.status_code == 200:
                    log.log(__name__, sys._getframe().f_code.co_name, 'download got: %s' % response.json(), log.LEVEL_DEBUG)
                    download = utils.json_to_download_object(response.json())
                else:
                    log.log(__name__, sys._getframe().f_code.co_name, 'Error get %s => %s' % (response.status_code, response.json()),
                            log.LEVEL_ERROR)
            except Exception:
                import traceback

                log.log(__name__, sys._getframe().f_code.co_name, "Get download by id: No database connection => %s" %
                        traceback.format_exc().splitlines()[-1],
                        log.LEVEL_ERROR)
                log.log(__name__, sys._getframe().f_code.co_name, "Traceback: %s" % traceback.format_exc(), log.LEVEL_DEBUG)
        else:
            log.log(__name__, sys._getframe().f_code.co_name, 'Id is none', log.LEVEL_ERROR)

        return download

    @staticmethod
    def get_next(params):
        download = None
        try:
            if params is None:
                log.log(__name__, sys._getframe().f_code.co_name, config.application_configuration.rest_address + 'downloads/next', log.LEVEL_DEBUG)
                response = requests.get(config.application_configuration.rest_address + 'downloads/next')
            else:
                log.log(__name__, sys._getframe().f_code.co_name, config.application_configuration.rest_address + 'downloads/next => params: %s' % params, log.LEVEL_DEBUG)
                response = requests.get(config.application_configuration.rest_address + 'downloads/next', params=params)

            if response.status_code == 200:
                log.log(__name__, sys._getframe().f_code.co_name, 'download got: %s' % response.json(), log.LEVEL_DEBUG)
                download = utils.json_to_download_object(response.json())
            else:
                log.log(__name__, sys._getframe().f_code.co_name, 'Error get %s => %s' % (response.status_code, response.json()), log.LEVEL_ERROR)
        except Exception:
            import traceback

            log.log(__name__, sys._getframe().f_code.co_name, "Get next download: No database connection => %s" % traceback.format_exc().splitlines()[-1], log.LEVEL_ALERT)
            log.log(__name__, sys._getframe().f_code.co_name, "Traceback: %s" % traceback.format_exc(), log.LEVEL_ALERT)
        else:
            log.log(__name__, sys._getframe().f_code.co_name, 'Id is none', log.LEVEL_ERROR)

        return download

    @staticmethod
    def get_next_downloads():
        downloads_list = []

        try:
            response = requests.get(config.application_configuration.rest_address + 'downloads/next2')

            if response.status_code == 200:
                log.log(__name__, sys._getframe().f_code.co_name, 'downloads got: %s' % response.json(), log.LEVEL_DEBUG)
                downloads_list = utils.json_to_download_object_list(response.json())
            else:
                log.log(__name__, sys._getframe().f_code.co_name, 'Error get %s => %s' % (response.status_code, response.json()), log.LEVEL_ERROR)
        except:
            import traceback

            log.log(__name__, sys._getframe().f_code.co_name,
                    "Get next downloads: No database connection => %s" % traceback.format_exc().splitlines()[-1],
                    log.LEVEL_ALERT)
            log.log(__name__, sys._getframe().f_code.co_name, "Traceback: %s" % traceback.format_exc(), log.LEVEL_ALERT)

        return downloads_list

    @staticmethod
    def get_all_by_params(params):
        downloads_list = None
        if params is not None:
            try:
                log.log(__name__, sys._getframe().f_code.co_name,
                    config.application_configuration.rest_address + 'downloads => params: %s' % params,
                    log.LEVEL_DEBUG)
                response = requests.get(config.application_configuration.rest_address + 'downloads',
                                        params=params)

                if response.status_code == 200:
                    downloads_list = utils.json_to_download_object_list(response.json())
                else:
                    log.log(__name__, sys._getframe().f_code.co_name,
                        'Error get %s => %s' % (response.status_code, response.json()),
                        log.LEVEL_ERROR)
            except Exception:
                import traceback

                log.log(__name__, sys._getframe().f_code.co_name,
                    "Get all actions by params: No database connection => %s" %
                    traceback.format_exc().splitlines()[-1],
                    log.LEVEL_ERROR)
                log.log(__name__, sys._getframe().f_code.co_name, "Traceback: %s" % traceback.format_exc(),
                        log.LEVEL_DEBUG)
        else:
            log.log(__name__, sys._getframe().f_code.co_name, 'Params is none', log.LEVEL_ERROR)

        return downloads_list

    @staticmethod
    def insert(download_to_insert):
        log.log(__name__, sys._getframe().f_code.co_name,
            config.application_configuration.rest_address + 'downloads => params: %s' % download_to_insert.to_insert_json(),
            log.LEVEL_DEBUG)

        response = requests.post(config.application_configuration.rest_address + 'downloads', data=download_to_insert.to_insert_json())

        if response.status_code != 200:
            log.log(__name__, sys._getframe().f_code.co_name, 'Error insert %s => %s' % (response.status_code, response.json()),
                    log.LEVEL_ERROR)
            raise Exception(
                'Error insert %s => %s' % (response.status_code, response.json()))
        else:
            return DownloadResource.get(response.json()['id'])

    @staticmethod
    def update(download_to_update, to_update_in_database=True):
        download_to_update.lifecycle_update_date = datetime.utcnow().isoformat()

        try:
            download_updated = None

            log.log(__name__, sys._getframe().f_code.co_name, config.application_configuration.rest_address + 'downloads/%d => %s' % (
                download_to_update.id, download_to_update.to_update_object()), log.LEVEL_DEBUG)

            params = download_to_update.to_update_object()
            params["update"] = 'true' if to_update_in_database else 'false'
            response = requests.put(config.application_configuration.rest_address + 'downloads/%d' % download_to_update.id, data=params)

            if response.status_code != 200:
                log.log(__name__, sys._getframe().f_code.co_name, 'Error update %s => %s' % (response.status_code, response.json()),
                        log.LEVEL_ERROR)
                download_to_update.logs = "ERROR DURING DOWNLOAD UPDATE\r\n"
            else:
                download_updated = utils.json_to_download_object(response.json())

            return download_updated

        except:
            import traceback

            log.log(__name__, sys._getframe().f_code.co_name, "Update download: No database connection => %s" %
                    traceback.format_exc().splitlines()[-1],
                    log.LEVEL_ERROR)
            log.log(__name__, sys._getframe().f_code.co_name, "Traceback: %s" % traceback.format_exc(), log.LEVEL_DEBUG)
            raise
