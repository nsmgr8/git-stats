import json
import logging
import os
from collections import defaultdict
from datetime import datetime
from functools import partial
from multiprocessing import Pool

from . import utils, collectors

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
        self.update_repos()
        self.repo_summary()
        self.repo_lines()
        revisions = self.repo_activity()
        self.repo_files_history(revisions)
        self.repo_tags()
        self.repo_branches()
        self.repo_blame()

        self.save_last_update()

    def update_repos(self):
        prev_states = self.load_data('repos.json') or []
        repo_states = []
        repos = list(self.config.REPOSITORIES.items())

        with Pool(self.num_pools) as p:
            for result in p.imap_unordered(
                partial(collectors.update_repo, self.repos_dir),
                repos
            ):
                if result:
                    logger.info(f'{result["name"]} updated')
                    repo_states.append(result)

        prev = {r['name']: r for r in prev_states}
        curr = {r['name']: r for r in repo_states}
        self.repos = []
        for repo in curr:
            if prev.get(repo, {}).get('HEAD') != curr[repo]['HEAD']:
                self.repos.append(repo)

        repo_states = {**prev}
        repo_states.update(curr)

        if self.config.force:
            self.repos = list(repo_states)

        self.save_data(list(repo_states.values()), 'repos.json')

    def repo_summary(self):
        with Pool(self.num_pools) as p:
            for result in p.imap_unordered(
                partial(collectors.summary, self.repos_dir),
                self.repos
            ):
                self.save_data(result['data'], 'summary.json', result['repo'])
                logger.info(f'{result["repo"]} summary updated')

    def repo_activity(self):
        revisions = {}
        with Pool(self.num_pools) as p:
            for result in p.imap_unordered(
                partial(collectors.activity, self.repos_dir),
                self.repos
            ):
                revisions[result['repo']] = result['revisions']
                self.save_data(result['data'], 'activity.json', result['repo'])
                logger.info(f'{result["repo"]} activity updated')

        return revisions

    def repo_files_history(self, revisions):
        fname = 'files-history.json'

        for repo, revs in revisions.items():
            cache = self.load_data(fname, repo)
            revs_to_check = []
            if cache:
                data = cache
                revs_to_check = [rev for rev in revs
                                 if rev['revision'] not in cache]
            else:
                data = {}
                revs_to_check = revs

            with Pool(self.num_pools) as p:
                for result in p.imap_unordered(
                    partial(collectors.num_files, self.repos_dir, repo),
                    revs_to_check
                ):
                    data.update(result)

            self.save_data(data, fname, repo)
            logger.info(f'{repo} files history updated')

    def repo_lines(self):
        with Pool(self.num_pools) as p:
            for result in p.imap_unordered(
                partial(collectors.count_lines, self.repos_dir),
                self.repos
            ):
                self.save_data(result['data'], 'lines.json', result['repo'])
                logger.info(f'{result["repo"]} lines updated')

    def repo_tags(self):
        repo_tags = {}
        with Pool(self.num_pools) as p:
            for result in p.imap_unordered(
                partial(collectors.get_tags, self.repos_dir),
                self.repos
            ):
                repo_tags[result['repo']] = result['tags']

        for repo, tags in repo_tags.items():
            with Pool(self.num_pools) as p:
                for result in p.imap_unordered(
                    partial(collectors.get_timestamp, self.repos_dir, repo),
                    [t['revision'] for t in tags]
                ):
                    for t in tags:
                        if t['revision'] == result['revision']:
                            t['timestamp'] = result['timestamp']

            tags = sorted(tags, key=lambda x: -x['timestamp'])
            r = [t['revision'] for t in tags]

            for i in range(len(tags)):
                if i == len(tags) - 1:
                    cmd = f'shortlog -s {r[i]}'
                else:
                    cmd = f'shortlog -s {r[i]} ^{r[i+1]}'
                authors = []

                for line in utils.run_git(
                    self.repos_dir, repo, cmd
                ).splitlines():
                    commits, author = line.strip().split('\t', 1)
                    authors.append({'author': author, 'commits': int(commits)})
                    tags[i]['authors'] = authors

            self.save_data(tags, 'tags.json', repo)
            logger.info(f'{repo} tags updated')

    def repo_branches(self):
        repo_branches = {}
        with Pool(self.num_pools) as p:
            for result in p.imap_unordered(
                partial(collectors.get_branches, self.repos_dir),
                self.repos
            ):
                repo_branches[result['repo']] = result['branches']

        for repo, branches in repo_branches.items():
            branch_timestamps = []
            with Pool(self.num_pools) as p:
                for result in p.imap_unordered(
                    partial(collectors.get_timestamp, self.repos_dir, repo),
                    branches
                ):
                    branch_timestamps.append(result)

            branches = sorted(branch_timestamps, key=lambda x: -x['timestamp'])
            self.save_data(branches, 'branches.json', repo)
            logger.info(f'{repo} branches updated')

    def repo_blame(self):
        detect_moves = self.config.config.get(
            'GLOBAL', 'detect_move', fallback=''
        ).strip().split()

        for repo in self.repos:
            cache = self.load_data('files-authors.json', repo) or {}
            detect_move = repo in detect_moves

            files_to_blame = {}
            authors = {}
            for line in utils.run_git(
                self.repos_dir, repo,
                'ls-tree -r HEAD'
            ).splitlines():
                *_, revision, fname = line.split()
                if cache.get(fname, {}).get('revision') == revision:
                    authors[fname] = cache[fname]
                else:
                    files_to_blame[fname] = revision

            with Pool(self.num_pools) as p:
                for result in p.imap_unordered(
                    partial(collectors.get_blame, self.repos_dir, repo,
                            detect_move),
                    files_to_blame
                ):
                    authors[result['file']] = {
                        'authors': result['authors'],
                        'revision': files_to_blame[result['file']],
                    }

                    self.save_data(authors, 'files-authors.json', repo)

            authors_counts = {
                'lines': defaultdict(int),
                'files': defaultdict(int),
            }
            for values in authors.values():
                for author, lines in values['authors'].items():
                    authors_counts['lines'][author] += lines
                    authors_counts['files'][author] += 1

            self.save_data(authors_counts, 'authors.json', repo)
            logger.info(f'{repo} authors lines updated')

    def _prepare_workdir(self):
        workdir = self.config.GLOBAL['workdir']
        logger.debug(f'Working folder {workdir}')

        self._repos_dir = os.path.join(workdir, 'repos')
        self._data_dir = os.path.join(workdir, 'data')

        os.makedirs(self._repos_dir, exist_ok=True)
        os.makedirs(self._data_dir, exist_ok=True)

    @property
    def repos_dir(self):
        if not hasattr(self, '_repos_dir'):
            self._prepare_workdir()
        return self._repos_dir

    @property
    def data_dir(self):
        if not hasattr(self, '_data_dir'):
            self._prepare_workdir()
        return self._data_dir

    @property
    def num_pools(self):
        if not hasattr(self, '_num_pools'):
            try:
                self._num_pools = int(self.config.config.getint(
                    'GLOBAL', 'process_pools', fallback=os.cpu_count()
                ))
            except ValueError:
                self._num_pools = os.cpu_count()

        return self._num_pools

    def save_data(self, data, fname, folders=''):
        utils.save_json(data, self.data_dir, fname, folders)

    def load_data(self, fname, folders=''):
        try:
            fpath = os.path.join(self.data_dir, folders, fname)
            with open(fpath) as fh:
                return json.loads(fh.read())
        except Exception:
            return None

    def save_last_update(self):
        last_updated = int(datetime.utcnow().timestamp())
        self.save_data({'last_updated': last_updated}, 'last_update.json')
