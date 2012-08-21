import json


class Node(object):

    def __init__(self, **data):
        self.name = data['name']
        self.enabled = data.get('enabled', True)
        self.status = data.get('status', 'idle')
        self.owner = data.get('owner')

    def to_json(self):
        return json.dumps({'name': self.name,
                           'enabled': self.enabled,
                           'status': self.status,
                           'owner': self.owner})
