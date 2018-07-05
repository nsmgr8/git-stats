import json
import logging
import math
import os
import re
from collections import defaultdict
from datetime import datetime

from . import utils

logger = logging.getLogger(__name__)


def update_repo(workdir, repo):
    """
    Update a given repository to current state

    :param workdir: working root folder
    :param repo: a tuple (repo_name, repo_origin_path)
    :return: a dict {repo_name: current_head_info}
    """
    try:
        clone(workdir, *repo)
        utils.run_git(workdir, repo[0], 'pull --tags')
        head, timestamp, author = utils.run_git(
            workdir, repo[0],
            f'log --pretty=format:"%H %at %aN" -n1'
        ).split(' ', 2)
        first_commit = int(utils.run_git(
            workdir, repo[0],
            'log --reverse --pretty=format:"%at"'
        ).splitlines()[0])
        return {
            'name': repo[0],
            'HEAD': head,
            'date': int(timestamp),
            'start_date': int(first_commit),
            'author': author,
        }
    except Exception:
        logger.exception(f'update error for repo "{repo}"')
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


def get_blame(workdir, repo, detect_move, fname):
    authors = defaultdict(int)
    opts = '-C -C -C -M' if detect_move else ''

    try:
        for line in utils.run_git(
            workdir, repo, f'blame --line-porcelain {opts} -w {fname}'
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
