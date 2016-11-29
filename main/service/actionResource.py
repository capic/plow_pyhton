__author__ = 'vcapi'

import log
import config
import requests
import utils
import sys
from datetime import datetime, timedelta
from bean.downloadBean import Download


class ActionResource(object):
    @staticmethod
    def get(action_id):
        action = None
        if action_id is not None:
            try:
                log.log(__name__, sys._getframe().f_code.co_name, config.application_configuration.rest_address + 'actions/%d' % action_id, log.LEVEL_DEBUG)
                response = requests.get(config.application_configuration.rest_address + 'actions/%d' + action_id)

                if response.status_code == 200:
                    log.log(__name__, sys._getframe().f_code.co_name,  'action got: %s' % response.json(), log.LEVEL_DEBUG)
                    action = utils.json_to_action_object(response.json())
                else:
                    log.log(__name__, sys._getframe().f_code.co_name,  'Error get %s => %s' % (response.status_code, response.json()),
                            log.LEVEL_ERROR)
            except Exception:
                import traceback

                log.log(__name__, sys._getframe().f_code.co_name, "Get action by id: No database connection => %s" %
                        traceback.format_exc().splitlines()[-1],
                        log.LEVEL_ERROR)
                log.log(__name__, sys._getframe().f_code.co_name, "Traceback: %s" % traceback.format_exc(), log.LEVEL_DEBUG)
        else:
            log.log(__name__, sys._getframe().f_code.co_name,  'Id is none', log.LEVEL_ERROR)

        return action

    @staticmethod
    def get_all_by_params(params):
        action_list = None
        if params is not None:
            try:
                log.log(__name__, sys._getframe().f_code.co_name,  config.application_configuration.rest_address + 'actions => params: %s' % params, log.LEVEL_DEBUG)
                response = requests.get(config.application_configuration.rest_address + 'actions', params=params)

                if response.status_code == 200:
                    action_list = utils.json_to_action_object_list(response.json())
                else:
                    log.log(__name__, sys._getframe().f_code.co_name,  'Error get %s => %s' % (response.status_code, response.json()),
                            log.LEVEL_ERROR)
            except Exception:
                import traceback

                log.log(__name__, sys._getframe().f_code.co_name, "Get all actions by params: No database connection => %s" %
                        traceback.format_exc().splitlines()[-1],
                        log.LEVEL_ERROR)
                log.log(__name__, sys._getframe().f_code.co_name, "Traceback: %s" % traceback.format_exc(), log.LEVEL_DEBUG)
        else:
            log.log(__name__, sys._getframe().f_code.co_name,  'Params is none', log.LEVEL_ERROR)

        return action_list

    @staticmethod
    def insert(action_to_insert):
        action_inserted = None
        if action_to_insert is not None:
            try:
                log.log(__name__, sys._getframe().f_code.co_name,
                    config.application_configuration.rest_address + 'actions => params: %s' % action.to_insert_json(),
                    log.LEVEL_DEBUG)

                response = requests.post(config.application_configuration.rest_address + 'actions',
                                            data=action.to_insert_json())

                if response.status_code != 200:
                    log.log(__name__, sys._getframe().f_code.co_name,  'Error insert action, %s => %s' % (response.status_code, response.json()), log.LEVEL_ERROR)
                    raise Exception('Error insert action, %s => %s' % (response.status_code, response.json()))
                else:
                    action_inserted = utils.json_to_action_object(response.json())

            except Exception:
                import traceback
                log.log(__name__, sys._getframe().f_code.co_name, "Insert action: No database connection => %s" % traceback.format_exc().splitlines()[-1], log.LEVEL_ERROR)
                log.log(__name__, sys._getframe().f_code.co_name, "Traceback: %s" % traceback.format_exc(), log.LEVEL_DEBUG)

        else:
            log.log(__name__, sys._getframe().f_code.co_name, "Action is none", log.LEVEL_ERROR)

        return action_inserted

    @staticmethod
    def update(action_to_update):
        action_to_update.lifecycle_update_date = datetime.utcnow().isoformat()

        try:
            action_updated = None

            log.log(__name__, sys._getframe().f_code.co_name,  config.application_configuration.rest_address + 'actions/%d => %s' % (
                action_to_update.id, action_to_update.to_update_object()), log.LEVEL_DEBUG)

            response = requests.put(config.application_configuration.rest_address + 'actions/%d' % action_to_update.id,
                                    data=action_to_update.to_update_object())

            if response.status_code != 200:
                log.log(__name__, sys._getframe().f_code.co_name,  'Error update %s => %s' % (response.status_code, response.json()),
                        log.LEVEL_ERROR)
            else:
                action_updated = utils.json_to_action_object(response.json())

            return action_updated

        except Exception:
            import traceback

            log.log(__name__, sys._getframe().f_code.co_name, "Update download: No database connection => %s" %
                    traceback.format_exc().splitlines()[-1],
                    log.LEVEL_ERROR)
            log.log(__name__, sys._getframe().f_code.co_name, "Traceback: %s" % traceback.format_exc(), log.LEVEL_DEBUG)
            raise