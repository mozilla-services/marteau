import json


class Node(object):

    def __init__(self, **data):
        self.name = data['name']
        self.enabled = data.pop('enabled', True)
        self.status = data.pop('status', 'idle')
        self.owner = data.pop('owner', None)
        self.metadata = dict(data)

    def __getattr__(self, attr):
        return self.metadata[attr]

    def to_json(self):
        data = {'name': self.name,
                'enabled': self.enabled,
                'status': self.status,
                'owner': self.owner}
        data.update(self.metadata)
        return json.dumps(data)
