__author__ = 'vcapi'

import log
import config
import requests
import utils
from datetime import datetime, timedelta
from bean.downloadBean import Download


class PackageResource(object):
    @staticmethod
    def get(package_id):
        log.log('[PackageResource](get) +++', log.LEVEL_INFO)

        package = None
        if package_id is not None:
            try:
                log.log('[PackageResource](get) | ' + config.REST_ADRESSE + 'downloads/package/%d' % package_id, log.LEVEL_DEBUG)
                response = requests.get(config.REST_ADRESSE + 'downloads/package/%d' % package_id)

                if response.status_code == 200:
                    log.log('[PackageResource](get) | package got: %s' % response.json(), log.LEVEL_DEBUG)
                    download = utils.json_to_download_package_object(response.json())
                else:
                    log.log('[PackageResource](get) | Error get %s => %s' % (response.code, response.json()),
                            log.LEVEL_ERROR)
            except Exception:
                import traceback

                log.log("[PackageResource](get) | Get package by id: No database connection \r\n %s" %
                        traceback.format_exc().splitlines()[-1],
                        log.LEVEL_ERROR)
                log.log("[PackageResource](get) | Traceback: %s" % traceback.format_exc(), log.LEVEL_DEBUG)
        else:
            log.log('[PackageResource](get) | Id is none', log.LEVEL_ERROR)

        return package

    @staticmethod
    def insert(package_to_insert):
        log.log('[PackageResource](Insert) +++', log.LEVEL_INFO)

        package_inserted = None
        if package_to_insert is not None:
            try:
                log.log(
                    '[PackageResource](Insert) | ' + config.REST_ADRESSE + 'downloads/package \r\n params: %s' % package_to_insert.to_insert_json(), log.LEVEL_DEBUG)

                response = requests.post(config.REST_ADRESSE + 'downloads/package',
                                            data=package_to_insert.to_insert_json())

                if response.status_code != 200:
                    log.log('[PackageResource](Insert) | Error insert package %s => %s' % (response.status_code, response.json()), log.LEVEL_ERROR)
                    raise Exception('[PackageResource](Insert) | Error insert package %s => %s' % (response.status_code, response.json()))
                else:
                    package_inserted = utils.json_to_download_package_object(response.json())

            except Exception:
                import traceback
                log.log("[PackageResource](Insert) | Insert package: No database connection \r\n %s" % traceback.format_exc().splitlines()[-1], log.LEVEL_ERROR)
                log.log("[PackageResource](Insert) | Traceback: %s" % traceback.format_exc(), log.LEVEL_DEBUG)

        else:
            log.log("[PackageResource](Insert) | Package is none", log.LEVEL_ERROR)

        return package_inserted