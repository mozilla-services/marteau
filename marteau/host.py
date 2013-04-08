import json
from marteau.util import generate_key


class Host(object):

    def __init__(self, **data):
        self.name = data['name']
        self.user = data['user']
        self.key = data.get('key', generate_key())

    def to_json(self):
        data = {'name': self.name,
                'user': self.user,
                'key': self.key}
        data = data.items()
        data.sort()
        return json.dumps(data)

    @classmethod
    def from_json(cls, data):
        data = dict(json.loads(data))
        return cls(**data)
