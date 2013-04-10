import json
from marteau.util import generate_key, check_host


class Host(object):

    def __init__(self, **data):
        self.name = data['name']
        self.user = data['user']
        self.key = data.get('key', generate_key())
        self.verified = data.get('verified', False)

    def verify(self):
        self.verified = check_host(self.name, self.key)
        return self.verified

    def to_json(self):
        data = {'name': self.name,
                'user': self.user,
                'key': self.key,
                'verified': self.verified}
        data = data.items()
        data.sort()
        return json.dumps(data)

    @classmethod
    def from_json(cls, data):
        data = dict(json.loads(data))
        return cls(**data)
