__author__ = 'vcapi'

import log
import config
import requests
import utils
from datetime import datetime, timedelta
from bean.downloadBean import Download


class ActionResource(object):
    @staticmethod
    def get(action_id):
        log.log('[ActionResource](get) +++', log.LEVEL_INFO)

        action = None
        if action_id is not None:
            try:
                log.log('[ActionResource](get) | ' + config.REST_ADRESSE + 'actions/%d' % action_id, log.LEVEL_DEBUG)
                response = requests.get(config.REST_ADRESSE + 'actions/%d' + action_id)

                if response.status_code == 200:
                    log.log('[ActionResource](get) | action got: %s' % response.json(), log.LEVEL_DEBUG)
                    action = utils.json_to_action_object(response.json())
                else:
                    log.log('[ActionResource](get) | Error get %s => %s' % (response.code, response.json()),
                            log.LEVEL_ERROR)
            except Exception:
                import traceback

                log.log("[ActionResource](get) | Get action by id: No database connection \r\n %s" %
                        traceback.format_exc().splitlines()[-1],
                        log.LEVEL_ERROR)
                log.log("[ActionResource](get) | Traceback: %s" % traceback.format_exc(), log.LEVEL_DEBUG)
        else:
            log.log('[ActionResource](get) | Id is none', log.LEVEL_ERROR)

        return action

    @staticmethod
    def get_all_by_params(params):
        log.log('[ActionResource](get_all_by_params) +++', log.LEVEL_INFO)

        action_list = None
        if params is not None:
            try:
                log.log('[ActionResource](get_all_by_params) | ' + config.REST_ADRESSE + 'actions \r\n params: %s' % params, log.LEVEL_DEBUG)
                response = requests.get(config.REST_ADRESSE + 'actions', params=params)

                if response.status_code == 200:
                    action_list = utils.json_to_action_object_list(response.json())
                else:
                    log.log('[ActionResource](get_all_by_params) | Error get %s => %s' % (response.code, response.json()),
                            log.LEVEL_ERROR)
            except Exception:
                import traceback

                log.log("[ActionResource](get_all_by_params) | Get all actions by params: No database connection \r\n %s" %
                        traceback.format_exc().splitlines()[-1],
                        log.LEVEL_ERROR)
                log.log("[ActionResource](get_all_by_params) | Traceback: %s" % traceback.format_exc(), log.LEVEL_DEBUG)
        else:
            log.log('[ActionResource](get_all_by_params) | Params is none', log.LEVEL_ERROR)

        return action_list

    @staticmethod
    def insert(action_to_insert):
        log.log('[ActionResource](Insert) +++', log.LEVEL_INFO)

        action_inserted = None
        if action_to_insert is not None:
            try:
                log.log(
                    '[ActionResource](Insert) | ' + config.REST_ADRESSE + 'actions \r\n params: %s' % action.to_insert_json(),
                    log.LEVEL_DEBUG)

                response = requests.post(config.REST_ADRESSE + 'actions',
                                            data=action.to_insert_json())

                if response.status_code != 200:
                    log.log('[ActionResource](Insert) | Error insert action, %s => %s' % (response.status_code, response.json()), log.LEVEL_ERROR)
                    raise Exception('[ActionResource](Insert) | Error insert action, %s => %s' % (response.status_code, response.json()))
                else:
                    action_inserted = utils.json_to_action_object(response.json())

            except Exception:
                import traceback
                log.log("[ActionResource](Insert) | Insert action: No database connection \r\n %s" % traceback.format_exc().splitlines()[-1], log.LEVEL_ERROR)
                log.log("[ActionResource](Insert) | Traceback: %s" % traceback.format_exc(), log.LEVEL_DEBUG)

        else:
            log.log("[ActionResource](Insert) | Action is none", log.LEVEL_ERROR)

        return action_inserted

    @staticmethod
    def update(action_to_update):
        log.log('[ActionResource](update) +++', log.LEVEL_INFO)

        action_to_update.lifecycle_update_date = datetime.utcnow().isoformat()

        try:
            action_updated = None

            log.log('[ActionResource](update) | ' + config.REST_ADRESSE + 'actions/%d \r\n %s' % (
                action_to_update.id, action_to_update.to_update_object()), log.LEVEL_DEBUG)

            response = requests.put(config.REST_ADRESSE + 'actions/%d' % action_to_update.id,
                                    data=action_to_update.to_update_object())

            if response.status_code != 200:
                log.log('[ActionResource](update) | Error update %s => %s' % (response.code, response.json()),
                        log.LEVEL_ERROR)
            else:
                action_updated = utils.json_to_action_object(response.json())

            return action_updated

        except Exception:
            import traceback

            log.log("[DownloadResource](update) | Update download: No database connection \r\n %s" %
                    traceback.format_exc().splitlines()[-1],
                    log.LEVEL_ERROR)
            log.log("[DownloadResource](update) | Traceback: %s" % traceback.format_exc(), log.LEVEL_DEBUG)
            raise