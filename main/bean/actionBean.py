# coding: utf8

__author__ = 'Vincent'

import json


class Action:
    ACTION_MOVE = 1
    ACTION_UNRAR = 2

    PROPERTY_PERCENTAGE = 1
    PROPERTY_DIRECTORY_SRC = 2
    PROPERTY_DIRECTORY_DST = 3
    PROPERTY_TIME_LEFT = 4
    PROPERTY_TIME_ELAPSED = 5
    PROPERTY_TIME_TOTAL = 6

    def __init__(self):
        self.download_id = None
        self.action_type_id = None
        self.property_id = None
        self.num = None
        self.property_value = None
        self.lifecycle_insert_date = None
        self.lifecycle_update_date = None
        self.action_status_id = None
        self.directory = None

    def to_string(self):
        return 'download_id: %s | action_type_id: %s | property_id: %s | num: %s | property_value: %s | action_status_id: %s | directory_id: %s' % (
            str(self.downloadid), str(self.action_type_id), str(self.property_id), str(self.num), self.property_value,
            str(self.action_status_id), self.directory.to_string())

    def to_update_simple_json(self):
        return json.dumps({
            "download_id": self.download_id,
            "action_type_id": self.action_type_id,
            "property_id": self.property_id,
            "num": self.num,
            "property_value": self.property_value,
            "lifecycle_update_date": self.lifecycle_update_date,
            "action_status_id": self.action_status_id,
            "directory_id": self.directory.id if self.directory is not None else None})

    def to_update_json(self):
        return {
            "action":
                self.to_update_simple_json()
        }

    def to_insert_json(self):
        return {
            "action":
                json.dumps({
                    "download_id": self.download_id,
                    "action_type_id": self.action_type_id,
                    "property_id": self.property_id,
                    "num": self.num,
                    "property_value": self.property_value,
                    "lifecycle_insert_date": self.lifecycle_insert_date,
                    "lifecycle_update_date": self.lifecycle_update_date,
                    "action_status_id": self.action_status_id,
                    "directory_id": self.directory.id if self.directory is not None else None})
        }