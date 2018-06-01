import json
import logging
import os
import re
from datetime import datetime
from functools import partial
from multiprocessing import Pool

from . import utils

logger = logging.getLogger(__name__)


class GitStats:
    """
    Git Stats generator
    """
    def __init__(self, config):
        """
        :param config: config instance
        """
        self.config = config

    def run(self):
        """
        Main runner
        """
        self._prepare_workdir()

        self.load_repositories_info()
        self.repo_states = []
        repos = list(self.config.REPOSITORIES.items())

        with Pool(8) as p:
            for result in p.imap_unordered(partial(update_repo,
                                                   self.repos_dir),
                                           repos):
                if result:
                    self.repo_states.append(result)

        logger.info(self.repo_states)
        self.save_data(self.repo_states, 'repos.json')

        self.save_last_update()

    def _prepare_workdir(self):
        self.workdir = self.config.GLOBAL['workdir']
        logger.debug(f'Output folder {self.workdir}')

        self.repos_dir = os.path.join(self.workdir, 'repos')
        self.data_dir = os.path.join(self.workdir, 'data')

        os.makedirs(self.repos_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)

    def save_data(self, data, fname, folders=''):
        utils.save_json(data, self.data_dir, fname, folders)

    def load_repositories_info(self):
        repo_info_path = os.path.join(self.data_dir, 'repos.json')
        try:
            with open(repo_info_path) as fh:
                self.previous_states = json.loads(fh.read())
        except Exception:
            self.previous_states = []

    def save_last_update(self):
        last_updated = int(datetime.utcnow().timestamp())
        self.save_data({'last_updated': last_updated}, 'last_update.json')


def update_repo(workdir, repo):
    """
    Update a given repository to current state

    :param workdir: working root folder
    :param repo: a tuple (repo_name, repo_origin_path)
    :return: a dict {repo_name: current_head_info}
    """
    logger.debug(f'Current repository: {repo[0]} {repo[1]}')

    try:
        clone(workdir, *repo)
        utils.run_git(workdir, repo[0], 'pull --tags')
        head, timestamp, author = utils.run_git(
            workdir, repo[0],
            f'log --pretty=format:"%H %at %aN" -n1'
        ).split(' ', 2)
        return {
            'name': repo[0],
            'HEAD': head,
            'date': int(timestamp),
            'author': author,
        }
    except Exception as e:
        logger.error(e)
        return {}


def clone(workdir, repo_name, repo_path):
    """
    Clone current repository. It will fail silently if already cloned.
    """
    try:
        return utils.run(f'git clone {repo_path} {repo_name}', workdir)
    except Exception:
        pass
