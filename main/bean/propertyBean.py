

__author__ = 'Vincent'

import json


class Property:
    def __init__(self):
        self.action_id = None
        self.property_id = None
        self.property_value = None
        self.directory = None

    def to_string(self):
        return 'action_id: %s | property_id: %s | property_value: %s | directory: %s' % (
            str(self.action_id), str(self.property_id), self.property_value, self.directory.to_string())

    def to_update_json(self):
        return {
            "property":
                json.dumps({
                    "action_id": self.action_id,
                    "property_id": self.property_id,
                    "property_value": self.property_value,
                    "directory_id": self.directory.id if self.directory is not None else None})
        }

    def to_insert_json(self):
        return {
            "property":
                json.dumps({
                    "action_id": self.action_id,
                    "property_id": self.property_id,
                    "property_value": self.property_value,
                    "directory_id": self.directory.id if self.directory is not None else None})
        }