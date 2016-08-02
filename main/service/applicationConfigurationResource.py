__author__ = 'vcapi'

import log
import config
import requests
import utils
from datetime import datetime, timedelta
from bean.downloadBean import Download


class ApplicationConfigurationResource(object):
    @staticmethod
    def get(application_configuration_id):
        log.log('[ApplicationConfigurationResource](get) +++', log.LEVEL_INFO)

        application_configuration = None
        if application_configuration_id is not None:
            try:
                log.log(
                    '[ApplicationConfigurationResource](get) | ' + config.REST_ADRESSE + 'applicationConfiguration/%d' % application_configuration_id,
                    log.LEVEL_DEBUG)
                response = requests.get(
                    config.REST_ADRESSE + 'applicationConfiguration/%d' % application_configuration_id)

                if response.status_code == 200:
                    log.log(
                        '[ApplicationConfigurationResource](get) | application_configuration got: %s' % response.json(),
                        log.LEVEL_DEBUG)
                    application_configuration = utils.json_to_application_configuration_object(response.json())
                else:
                    log.log('[ApplicationConfigurationResource](get) | Error get %s => %s' % (
                        response.code, response.json()),
                            log.LEVEL_ERROR)
            except Exception:
                import traceback

                log.log(
                    "[ApplicationConfigurationResource](get) | "
                    "Get application configuration by id: No database connection \r\n %s" %
                    traceback.format_exc().splitlines()[-1],
                    log.LEVEL_ERROR)
                log.log("[ApplicationConfigurationResource](get) | Traceback: %s" % traceback.format_exc(),
                        log.LEVEL_DEBUG)
        else:
            log.log('[ApplicationConfigurationResource](get) | Id is none', log.LEVEL_ERROR)

        return application_configuration
