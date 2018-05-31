import logging
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
        self.workdir = self.config.GLOBAL['workdir']
        logger.debug(f'Output folder {self.workdir}')

        repo_states = {}
        repos = list(self.config.REPOSITORIES.items())

        with Pool(8) as p:
            for task in p.imap_unordered(partial(update_repo, self.workdir),
                                         repos):
                repo_states.update(task)

        logger.info(repo_states)


def update_repo(workdir, repo):
    """
    Update a given repository to current state

    :param workdir: working root folder
    :param repo: a tuple (repo_name, repo_origin_path)
    :return: a dict {repo_name: current_head_sha}
    """
    logger.debug(f'Current repository: {repo[0]} {repo[1]}')

    try:
        clone(workdir, *repo)
        run_git(workdir, repo[0], 'pull --tags')
        head = run_git(workdir, repo[0], 'rev-parse HEAD')
        return {repo[0]: head}
    except Exception as e:
        logger.error(e)
        return {}


def clone(workdir, repo_name, repo_path):
    """
    Clone current repository. It will fail silently if already cloned.
    """
    try:
        return run(f'mkdir -p {workdir}/repos && '
                   f'cd {workdir}/repos && '
                   f'git clone {repo_path} {repo_name}')
    except Exception:
        pass
