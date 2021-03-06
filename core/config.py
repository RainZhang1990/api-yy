import os.path

import yaml

from core.singleton import Singleton


class Config(metaclass=Singleton):
    def __init__(self):
        self.config = dict()
        filepaths = ['config.yaml', os.path.join('.', 'config', 'config.yaml')]
        self.load_config(filepaths)

    def load_config(self, filepaths):
        if not filepaths:
            raise Exception('filepaths is required')

        for filepath in filepaths:
            if os.path.isfile(filepath):
                with open(filepath, 'r', encoding='utf-8') as file:
                    self.config = yaml.load(file, Loader=yaml.FullLoader)
                break

        if not self.config:
            raise Exception('a valid config filed is required')

    def __getattr__(self, item):
        return self.config.get(item)
