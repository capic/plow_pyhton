__author__ = 'vcapi'

import log
import config
import requests
import utils
import sys
from datetime import datetime, timedelta
from bean.downloadBean import Download


class ApplicationConfigurationResource(object):
    @staticmethod
    def get(application_configuration_id, download=None):
        application_configuration = None
        if application_configuration_id is not None:
            try:
                log.log(__name__, sys._getframe().f_code.co_name, config.application_configuration.rest_address + 'applicationConfiguration/%d' % application_configuration_id, log.LEVEL_DEBUG)
                response = requests.get(config.application_configuration.rest_address + 'applicationConfiguration/%d' % application_configuration_id)

                if response.status_code == 200:
                    log.log(__name__, sys._getframe().f_code.co_name, 'application_configuration got: %s' % response.json(), log.LEVEL_INFO, True, download)
                    application_configuration = utils.json_to_application_configuration_object(response.json())
                else:
                    log.log(__name__, sys._getframe().f_code.co_name, 'Error get %s => %s' % (response.status_code, response.json()), log.LEVEL_ERROR, True, download)
            except Exception:
                import traceback

                log.log(__name__, sys._getframe().f_code.co_name, "Get application configuration by id: No database connection => %s" % traceback.format_exc().splitlines()[-1], log.LEVEL_ALERT, True, download)
                log.log(__name__, sys._getframe().f_code.co_name, "Traceback: %s" % traceback.format_exc(), log.LEVEL_ALERT, True, download)
        else:
            log.log(__name__, sys._getframe().f_code.co_name, 'Id is none', log.LEVEL_ERROR, True, download)

        return application_configuration
