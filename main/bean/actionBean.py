# coding: utf8

__author__ = 'Vincent'

import json


class Action:
    ACTION_MOVE_DOWNLOAD = 1
    ACTION_UNRAR_PACKAGE = 2
    ACTION_RENAME_DOWNLOAD = 4

    PROPERTY_PERCENTAGE = 1
    PROPERTY_DIRECTORY_SRC = 2
    PROPERTY_DIRECTORY_DST = 3
    PROPERTY_TIME_LEFT = 4
    PROPERTY_TIME_ELAPSED = 5
    PROPERTY_TIME_TOTAL = 6

    STATUS_WAITING = 1
    STATUS_IN_PROGRESS = 2
    STATUS_FINISHED = 3
    STATUS_ERROR = 4

    TARGET_DOWNLOAD = 1
    TARGET_PACKAGE = 2

    def __init__(self):
        self.id = None
        self.lifecycle_insert_date = None
        self.lifecycle_update_date = None
        self.download_id = None
        self.download_package_id = None
        self.action_status_id = None
        self.action_type_id = None
        self.properties = None

    def to_string(self):
        return 'id: %s | download_id: %s | download_package_id: %s | action_status_id: %s | action_type_id: %s ' % (
            str(self.id), str(self.download_id), str(self.download_package_id), str(self.action_status_id), str(self.action_type_id))

    def to_update_json(self):
        return {
            "action":
                json.dumps({
                    "id": self.id,
                    "lifecycle_update_date": self.lifecycle_update_date,
                    "action_status_id": self.action_status_id,
                    "action_has_properties": self.properties})
        }

    # def to_insert_json(self):
    #     return {
    #         "action":
    #             json.dumps({
    #                 "download_id": self.download_id,
    #                 "action_type_id": self.action_type_id,
    #                 "property_id": self.property_id,
    #                 "num": self.num,
    #                 "property_value": self.property_value,
    #                 "lifecycle_insert_date": self.lifecycle_insert_date,
    #                 "lifecycle_update_date": self.lifecycle_update_date,
    #                 "action_status_id": self.action_status_id,
    #                 "directory_id": self.directory.id if self.directory is not None else None})
    #     }