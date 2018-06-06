import json
import logging
import math
import os
import re
from collections import defaultdict
from datetime import datetime
from functools import partial
from multiprocessing import Pool

from . import utils

logger = logging.getLogger(__name__)
num_pools = max(os.cpu_count() - 1, 1)


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

        with Pool(num_pools) as p:
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

        if self.config.force:
            self.repos = list(repo_states)

        logger.info(repo_states)
        self.save_data(list(repo_states.values()), 'repos.json')

    def repo_summary(self):
        with Pool(num_pools) as p:
            for result in p.imap_unordered(partial(summary, self.repos_dir),
                                           self.repos):
                logger.info(result)
                self.save_data(result['data'], 'summary.json', result['repo'])

    def repo_activity(self):
        revisions = {}
        with Pool(num_pools) as p:
            for result in p.imap_unordered(partial(activity, self.repos_dir),
                                           self.repos):
                logger.info(result)
                revisions[result['repo']] = result['revisions']
                self.save_data(result['data'], 'activity.json', result['repo'])

        return revisions

    def repo_files_history(self, revisions):
        fname = 'files-history.json'

        for repo, revs in revisions.items():
            cache = self.load_data(fname, repo)
            revs_to_check = []
            if cache:
                data = cache
                revs_to_check = [rev for rev in revs
                                 if rev not in revs]
            else:
                data = {}
                revs_to_check = revs

            with Pool(num_pools) as p:
                for result in p.imap_unordered(partial(num_files,
                                                       self.repos_dir, repo),
                                               revs_to_check):
                    data.update(result)

            logger.info(data)
            self.save_data(data, fname, repo)

    def repo_lines(self):
        with Pool(num_pools) as p:
            for result in p.imap_unordered(partial(count_lines,
                                                   self.repos_dir),
                                           self.repos):
                logger.info(result)
                self.save_data(result['data'], 'lines.json', result['repo'])

    def repo_tags(self):
        repo_tags = {}
        with Pool(num_pools) as p:
            for result in p.imap_unordered(partial(get_tags,
                                                   self.repos_dir),
                                           self.repos):
                repo_tags[result['repo']] = result['tags']

        for repo, tags in repo_tags.items():
            with Pool(num_pools) as p:
                for result in p.imap_unordered(partial(get_timestamp,
                                                       self.repos_dir, repo),
                                               [t['revision'] for t in tags]):
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
            logger.info(tags)

    def repo_branches(self):
        repo_branches = {}
        with Pool(num_pools) as p:
            for result in p.imap_unordered(partial(get_branches,
                                                   self.repos_dir),
                                           self.repos):
                repo_branches[result['repo']] = result['branches']

        for repo, branches in repo_branches.items():
            branch_timestamps = []
            with Pool(num_pools) as p:
                for result in p.imap_unordered(partial(get_timestamp,
                                                       self.repos_dir, repo),
                                               branches):
                    branch_timestamps.append(result)

            branches = sorted(branch_timestamps, key=lambda x: -x['timestamp'])
            self.save_data(branches, 'branches.json', repo)
            logger.info(branches)

    def repo_blame(self):
        for repo in self.repos:
            cache = self.load_data('files-authors.json', repo) or {}

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

            with Pool(num_pools) as p:
                for result in p.imap_unordered(partial(get_blame,
                                                       self.repos_dir, repo),
                                               files_to_blame):
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

            logger.info(f'{repo}: {authors_counts}')
            self.save_data(authors_counts, 'authors.json', repo)

    def _prepare_workdir(self):
        self.workdir = self.config.GLOBAL['workdir']
        logger.debug(f'Output folder {self.workdir}')

        self.repos_dir = os.path.join(self.workdir, 'repos')
        self.data_dir = os.path.join(self.workdir, 'data')

        os.makedirs(self.repos_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)

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
    age = math.ceil((latest_commit - first_commit) / 60 / 60 / 24)
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


def activity(workdir, repo):
    hour_of_week = defaultdict(lambda: defaultdict(int))
    by_time = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    authors = defaultdict(
        lambda: defaultdict(
            lambda: defaultdict(
                lambda: defaultdict(int)
            )
        )
    )
    authors_age = defaultdict(lambda: defaultdict(int))

    revisions = []
    for line in utils.run_git(
        workdir, repo,
        'log --shortstat --pretty=format:"%at %T %aN" HEAD'
    ).splitlines():
        line = line.strip()
        if not line:
            continue

        data = {}
        m = re.search(r'\d+ files? changed,', line)
        if m:
            m = re.search(r' (\d+) insert', line)
            if m:
                data['insertions'] = int(m.groups()[0])
            m = re.search(r' (\d+) delet', line)
            if m:
                data['deletions'] = int(m.groups()[0])
        else:
            data['commits'] = 1
            timestamp, revision, author = line.split(' ', 2)
            timestamp = int(timestamp)
            revisions.append({'timestamp': timestamp, 'revision': revision})

            date = datetime.fromtimestamp(timestamp)
            month = date.strftime('%Y-%m')
            day = date.strftime('%Y-%m-%d')
            week = date.strftime('%Y-%V')

            hour_of_week[date.weekday()][date.hour] += 1

            if (
                authors_age[author]['first_commit'] == 0 or
                authors_age[author]['first_commit'] > timestamp
            ):
                authors_age[author]['first_commit'] = timestamp

            if authors_age[author]['last_commit'] < timestamp:
                authors_age[author]['last_commit'] = timestamp

        for ktype, kvalue in (
            ('yearly', date.year),
            ('monthly', month),
            ('daily', day),
            ('weekly', week),
            ('at_hour', date.hour),
        ):
            for key, value in data.items():
                by_time[ktype][key][kvalue] += value
                authors[author][ktype][key][kvalue] += value

    for author in authors_age:
        authors_age[author]['days'] = math.ceil((
            authors_age[author]['last_commit'] -
            authors_age[author]['first_commit']
        ) / 60 / 60 / 24)

    return {
        'data': {
            'by_time': {k: dict(v) for k, v in by_time.items()},
            'hour_of_week': {k: dict(v) for k, v in hour_of_week.items()},
            'by_authors': {k: {kk: dict(vv) for kk, vv in v.items()}
                           for k, v in authors.items()},
            'authors_age': {k: dict(v) for k, v in authors_age.items()},
        },
        'revisions': revisions,
        'repo': repo,
    }


def count_lines(workdir, repo):
    try:
        lines = json.loads(utils.run(f'cloc --vcs git --json',
                           os.path.join(workdir, repo)).stdout.strip())
    except Exception:
        lines = []

    return {
        'data': {
            'lines': lines,
        },
        'repo': repo,
    }


def num_files(workdir, repo, revision):
    files = len(utils.run_git(
        workdir, repo,
        f'ls-tree -r --name-only {revision["revision"]}'
    ).splitlines())
    return {
        revision['revision']: {
            'timestamp': revision['timestamp'],
            'files': files,
        },
    }


def get_tags(workdir, repo):
    try:
        tags = []

        for line in utils.run_git(
            workdir, repo,
            f'show-ref --tags'
        ).splitlines():
            revision, tag = line.split()
            tag = tag.replace('refs/tags/', '')
            tags.append({'tag': tag, 'revision': revision})

    except Exception:
        tags = []

    return {
        'tags': tags,
        'repo': repo,
    }


def get_branches(workdir, repo):
    branches = []
    for line in utils.run_git(workdir, repo, 'branch -r').splitlines():
        line = line.strip()
        if 'HEAD' in line:
            continue

        branches.append(line)

    return {
        'branches': branches,
        'repo': repo,
    }


def get_blame(workdir, repo, fname):
    authors = defaultdict(int)

    try:
        for line in utils.run_git(
            workdir, repo, f'blame --line-porcelain -w {fname}'
        ).splitlines():
            if line.startswith('author '):
                _, author = line.split(' ', 1)
                authors[author] += 1
    except Exception:
        pass

    return {'file': fname, 'authors': dict(authors)}


def get_timestamp(workdir, repo, revision):
    timestamp = utils.run_git(workdir, repo,
                              f'log --pretty=format:"%at" -n 1 {revision}')
    return {
        'timestamp': int(timestamp),
        'revision': revision,
    }
