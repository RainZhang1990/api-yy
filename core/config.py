import os.path

import yaml

from core.singleton import Singleton


class Config(metaclass=Singleton):
    def __init__(self):
        self.config = dict()

    def load_config(self, filepaths):
        """should call before access config values

        Arguments:
            filepaths list -- config file path list.
        """
        if not filepaths:
            raise Exception('filepaths is required')

        # load config
        for filepath in filepaths:
            if os.path.isfile(filepath):
                with open(filepath, 'r', encoding='utf-8') as file:
                    self.config = yaml.load(file)
                break

        if not self.config:
            raise Exception('a valid config filed is required')

    def __getattr__(self, item):
        return self.config.get(item)


class Secret(metaclass=Singleton):
    def __init__(self):
        self.secret = dict()

    def load_secret(self, name, keys, paths):
        if not paths:
            raise Exception('secret paths is required')

        if not keys:
            raise Exception('key list is required')

        # get keypath
        keypath = ""
        for path in paths:
            if os.path.isdir(os.path.join(path, name)):
                keypath = os.path.join(path, name)
                break

        if keypath == "":
            raise Exception('path for secret:{} is not found'.format(name))

        # read values for keys
        secrets = dict()
        for key in keys:
            value = self._read_key_file(keypath, key)
            secrets[key] = value

        self.secret[name] = secrets

    def __getattr__(self, name):
        return self.secret.get(name)

    def _read_key_file(self, keypath, key):
        with open(os.path.join(keypath, key), 'r') as keyfile:
            return keyfile.read()
