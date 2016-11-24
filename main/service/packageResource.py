__author__ = 'vcapi'

import log
import config
import requests
import utils
import sys
from datetime import datetime, timedelta
from bean.downloadBean import Download


class PackageResource(object):
    @staticmethod
    def get(package_id):
        package = None
        if package_id is not None:
            try:
                log.log(__name__, sys._getframe().f_code.co_name, config.application_configuration.rest_address + 'downloads/package/%d' % package_id, log.LEVEL_DEBUG)
                response = requests.get(config.application_configuration.rest_address + 'downloads/package/%d' % package_id)

                if response.status_code == 200:
                    log.log(__name__, sys._getframe().f_code.co_name, 'package got: %s' % response.json(), log.LEVEL_DEBUG)
                    download = utils.json_to_download_package_object(response.json())
                else:
                    log.log(__name__, sys._getframe().f_code.co_name, 'Error get %s => %s' % (response.status_code, response.json()),
                            log.LEVEL_ERROR)
            except Exception:
                import traceback

                log.log(__name__, sys._getframe().f_code.co_name, "Get package by id: No database connection => %s" %
                        traceback.format_exc().splitlines()[-1],
                        log.LEVEL_ERROR)
                log.log(__name__, sys._getframe().f_code.co_name, "Traceback: %s" % traceback.format_exc(), log.LEVEL_DEBUG)
        else:
            log.log(__name__, sys._getframe().f_code.co_name, 'Id is none', log.LEVEL_ERROR)

        return package

    @staticmethod
    def insert(package_to_insert):
        package_inserted = None
        if package_to_insert is not None:
            try:
                log.log(__name__, sys._getframe().f_code.co_name,
                    config.application_configuration.rest_address + 'downloads/package => params: %s' % package_to_insert.to_insert_json(), log.LEVEL_DEBUG)

                response = requests.post(config.application_configuration.rest_address + 'downloads/package',
                                            data=package_to_insert.to_insert_json())

                if response.status_code != 200:
                    log.log(__name__, sys._getframe().f_code.co_name, 'Error insert package %s => %s' % (response.status_code, response.json()), log.LEVEL_ERROR)
                    raise Exception('Error insert package %s => %s' % (response.status_code, response.json()))
                else:
                    package_inserted = utils.json_to_download_package_object(response.json())

            except Exception:
                import traceback
                log.log(__name__, sys._getframe().f_code.co_name, "Insert package: No database connection => %s" % traceback.format_exc().splitlines()[-1], log.LEVEL_ERROR)
                log.log(__name__, sys._getframe().f_code.co_name, "Traceback: %s" % traceback.format_exc(), log.LEVEL_DEBUG)

        else:
            log.log(__name__, sys._getframe().f_code.co_name, "Package is none", log.LEVEL_ERROR)

        return package_inserted