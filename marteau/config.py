import os
import yaml

from marteau.fixtures import get_fixture


class MarteauConfig(dict):

    # XXX ????
    def lookup_modules(self):
        # we just want to lookup the modules, not return them.  that's to be
        # sure we're loading the plugins in the plugin system, if any.
        for module in self['lookup']:
            importlib.import_module(module)

    def get_fixture(self, name):
        data = self['fixtures'].get(name)
        fixture = get_fixture(data['class'])
        return fixture(self, **data.get('arguments', {}))


def read_yaml_config(project_dir, filename='.marteau.yml'):
    config_file = os.path.join(project_dir, filename)
    with open(config_file) as f:
        return MarteauConfig(yaml.safe_load(f.read()))
