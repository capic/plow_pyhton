__author__ = 'vcapi'

import log
import config
import requests
import utils
from datetime import datetime, timedelta
from bean.downloadBean import Download


class DirectoryResource(object):
    @staticmethod
    def get(directory_id):
        log.log('[DirectoryResource](get) +++', log.LEVEL_INFO)

        directory = None
        if directory_id is not None:
            try:
                log.log('[DirectoryResource](get) | ' + config.REST_ADRESSE + 'downloadDirectories/%d' + directory_id, log.LEVEL_DEBUG)
                response = requests.get(config.REST_ADRESSE + 'downloadDirectories/%d' + directory_id)

                if response.status_code == 200:
                    log.log('[DirectoryResource](get) | package got: %s' % response.json(), log.LEVEL_DEBUG)
                    directory = utils.json_to_download_directory_object(response.json())
                else:
                    log.log('[DirectoryResource](get) | Error get %s => %s' % (response.status_code, response.json()),
                            log.LEVEL_ERROR)
            except Exception:
                import traceback

                log.log("[DirectoryResource](get) | Get directory by id: No database connection \r\n %s" %
                        traceback.format_exc().splitlines()[-1],
                        log.LEVEL_ERROR)
                log.log("[DirectoryResource](get) | Traceback: %s" % traceback.format_exc(), log.LEVEL_DEBUG)
        else:
            log.log('[DirectoryResource](get) | Id is none', log.LEVEL_ERROR)

        return directory