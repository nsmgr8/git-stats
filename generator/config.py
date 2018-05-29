import os
from configparser import ConfigParser

from .utils import PROJECT_DIR


class Config:
    """
    A convenient class holding Confguration wrapping ConfigParser
    """
    _config = None

    def __init__(self, config_path=''):
        """
        :param config_path: if not given, defaults to project root config.ini
            file
        """
        self.config_path = config_path or os.path.join(PROJECT_DIR,
                                                       'config.ini')

    @property
    def config(self):
        """
        The ConfigParser object
        """
        if isinstance(self._config, ConfigParser):
            return self._config

        self._config = ConfigParser()
        self._config.read(self.config_path)
        return self._config

    def __getattr__(self, name):
        """
        Convenient object dot accessor to config section
        """
        return self.config[name]
