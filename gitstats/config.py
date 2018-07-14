import os
from configparser import ConfigParser

from .utils import PROJECT_DIR


class Config:
    """
    A convenient class holding Confguration wrapping ConfigParser
    """
    _config = None

    def __init__(self, *, config_path='', force=False, **kwargs):
        """
        :param config_path: if not given, defaults to project root config.ini
            file
        """
        self.force = force
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

    def repositories(self):
        """
        Parse the repositories config
        """
        repos = {}
        for repo_id, conf in self.REPOSITORIES.items():
            repo = {}
            for line in conf.strip().splitlines():
                key, _, val = [x.strip() for x in line.strip().partition(':')]
                if key and val:
                    repo[key] = val
            if 'clone' in repo:
                repos[repo_id] = repo
        return repos
