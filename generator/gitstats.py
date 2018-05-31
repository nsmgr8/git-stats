import logging
import os
from functools import partial
from multiprocessing import Pool

from .utils import run, run_git

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

        repo_states = {}
        repos = list(self.config.REPOSITORIES.items())

        with Pool(8) as p:
            for task in p.imap_unordered(partial(update_repo, self.repos_dir),
                                         repos):
                repo_states.update(task)

        logger.info(repo_states)

    def _prepare_workdir(self):
        self.workdir = self.config.GLOBAL['workdir']
        logger.debug(f'Output folder {self.workdir}')

        self.repos_dir = os.path.join(self.workdir, 'repos')
        self.data_dir = os.path.join(self.workdir, 'data')

        os.makedirs(self.repos_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)


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
        run_git(workdir, repo[0], 'pull --tags')
        head, timestamp, author = run_git(
            workdir, repo[0],
            f'log --pretty=format:"%H %at %aN" -n1'
        ).split(' ', 2)
        return {
            repo[0]: {
                'HEAD': head,
                'Date': int(timestamp),
                'Author': author,
            },
        }
    except Exception as e:
        logger.error(e)
        return {}


def clone(workdir, repo_name, repo_path):
    """
    Clone current repository. It will fail silently if already cloned.
    """
    try:
        return run(f'cd {workdir} && '
                   f'git clone {repo_path} {repo_name}')
    except Exception:
        pass
