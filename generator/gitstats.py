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

        self.update_repos()
        self.repo_summary()

        self.save_last_update()

    def update_repos(self):
        prev_states = self.load_repositories_info()
        repo_states = []
        repos = list(self.config.REPOSITORIES.items())

        with Pool(8) as p:
            for result in p.imap_unordered(partial(update_repo,
                                                   self.repos_dir),
                                           repos):
                if result:
                    repo_states.append(result)

        prev = {r['name']: r for r in prev_states}
        curr = {r['name']: r for r in repo_states}
        self.repos = []
        for repo in curr:
            if prev.get(repo, {}).get('HEAD') != curr[repo]['HEAD']:
                self.repos.append(repo)

        repo_states = {**prev}
        repo_states.update(curr)

        logger.info(repo_states)
        self.save_data(list(repo_states.values()), 'repos.json')

    def repo_summary(self):
        with Pool(8) as p:
            for result in p.imap_unordered(partial(summary, self.repos_dir),
                                           self.repos):
                logger.info(result)
                self.save_data(result['data'], 'summary.json', result['repo'])

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
        try:
            with open(os.path.join(self.data_dir, 'repos.json')) as fh:
                return json.loads(fh.read())
        except Exception:
            return []

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


def summary(workdir, repo):
    empty_sha = utils.empty_git_sha(workdir, repo)
    output = utils.run_git(workdir, repo, f'diff --shortstat {empty_sha}')
    files, lines = re.search(r'(\d+) .*, (\d+) .*', output).groups()
    authors = len(utils.run_git(workdir, repo, 'shortlog -s').splitlines())
    commits = utils.run_git(workdir, repo, 'rev-list --count HEAD')
    branches = len([x for x in utils.run_git(workdir, repo,
                                             'branch -r').splitlines()
                    if 'HEAD' not in x])
    first_commit = int(utils.run_git(
        workdir, repo,
        'log --reverse --pretty=format:"%at"'
    ).splitlines()[0])
    latest_commit = int(utils.run_git(workdir, repo,
                                      'log --pretty=format:"%at" -n1'))
    age = int((latest_commit - first_commit) / 60 / 60 / 24)
    try:
        tags = len(utils.run_git(workdir, repo,
                                 'show-ref --tags').splitlines())
    except Exception:
        tags = 0

    return {
        'data': [
            {'key': 'files', 'value': files},
            {'key': 'lines', 'value': lines, 'notes': 'includes empty lines'},
            {'key': 'authors', 'value': authors},
            {'key': 'commits', 'value': commits, 'notes': 'master only'},
            {'key': 'branches', 'value': branches},
            {'key': 'tags', 'value': tags},
            {'key': 'age', 'value': age, 'notes': 'active days since creation'},
        ],
        'repo': repo,
    }
