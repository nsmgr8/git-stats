import json
import os
from datetime import datetime
from multiprocessing.dummy import Pool
from tempfile import NamedTemporaryFile as tf, TemporaryDirectory as td

import pytest

from . import gitstats, config, collectors, utils

gitstats.Pool = Pool


@pytest.fixture()
def stat():
    with td(prefix='gitstats') as d, tf(prefix='gitstats') as f:
        f.write(f"""
        [GLOBAL]
        workdir = {d}

        [REPOSITORIES]
        repo1 = https://a-git.repo/repo1
        repo2 = https://a-git.repo/repo2
        """.encode())
        f.flush()

        cfg = config.Config(config_path=f.name, force=True)
        cfg.config

        yield {
            'cls': gitstats.GitStats(cfg),
            'workdir': d,
            'cfg': cfg,
        }


def test_repos_dir(stat):
    assert stat['cls'].repos_dir == stat['workdir'] + '/repos'


def test_data_dir(stat):
    assert stat['cls'].data_dir == stat['workdir'] + '/data'


def test_process_pools(stat):
    assert stat['cls'].num_pools == os.cpu_count()


def test_save_and_load_data(stat):
    data = {'foo': 'bar'}

    gs = stat['cls']
    assert gs.load_data('does-not-exist.json') is None

    # save data on root folder
    fname = 'test.json'
    gs.save_data(data, fname)

    fpath = os.path.join(gs.data_dir, fname)
    assert os.path.isfile(fpath)

    with open(fpath) as fh:
        assert json.loads(fh.read()) == data

    assert gs.load_data(fname) == data

    # save data in a folder
    gs.save_data(data, fname, 'f1')

    fpath = os.path.join(gs.data_dir, 'f1', fname)
    assert os.path.isfile(fpath)

    with open(fpath) as fh:
        assert json.loads(fh.read()) == data

    assert gs.load_data(fname, 'f1') == data

    # save data in nested folder
    gs.save_data(data, fname, ['f1', 'f2'])

    fpath = os.path.join(gs.data_dir, 'f1', 'f2', fname)
    assert os.path.isfile(fpath)

    with open(fpath) as fh:
        assert json.loads(fh.read()) == data

    assert gs.load_data(fname, 'f1/f2') == data


def test_last_update(stat):
    gs = stat['cls']

    start = int(datetime.utcnow().timestamp())

    gs.save_last_update()
    data = gs.load_data('last_update.json')

    end = int(datetime.utcnow().timestamp())

    assert start <= data['last_updated'] <= end


def test_run(stat, mocker):
    mocker.patch('subprocess.run')

    start = int(datetime.utcnow().timestamp())

    gs = stat['cls']

    methods = [
        'update_repos',
        'repo_summary',
        'repo_lines',
        'repo_activity',
        'repo_files_history',
        'repo_tags',
        'repo_branches',
        'repo_blame',
    ]
    for m in methods:
        mocker.spy(gs, m)

    gs.run()

    for m in methods:
        assert getattr(gs, 'update_repos').call_count == 1

    data = gs.load_data('last_update.json')

    end = int(datetime.utcnow().timestamp())

    assert start <= data['last_updated'] <= end


def test_update_repos(stat, mocker):
    _tmp = collectors.update_repo

    collectors.update_repo = mocker.Mock()
    collectors.update_repo.side_effect = [
        {'name': 'repo1', 'HEAD': 'repo1'},
        {'name': 'repo2', 'HEAD': 'repo2'},
    ]

    gs = stat['cls']
    gs.update_repos()

    assert gs.repos == ['repo1', 'repo2']

    collectors.update_repo = _tmp


def test_summary(stat, mocker):
    _tmp = collectors.summary

    collectors.summary = mocker.Mock()
    collectors.summary.side_effect = [
        {'repo': 'repo1', 'data': 'data1'},
        {'repo': 'repo2', 'data': 'data2'},
    ]

    gs = stat['cls']
    gs.repos = ['repo1', 'repo2']
    gs.repo_summary()

    assert gs.load_data('summary.json', 'repo1') == 'data1'
    assert gs.load_data('summary.json', 'repo2') == 'data2'

    collectors.summary = _tmp


def test_activity(stat, mocker):
    _tmp = collectors.activity

    data1 = {'by_authors': {'nasim': {}}}
    data2 = {'by_authors': {'someone': {}}}
    collectors.activity = mocker.Mock()
    collectors.activity.side_effect = [
        {'repo': 'repo1', 'data': data1, 'revisions': ['r1', 'r2']},
        {'repo': 'repo2', 'data': data2, 'revisions': ['r3']},
    ]

    gs = stat['cls']
    gs.repos = ['repo1', 'repo2']
    gs.save_data([{'key': 'authors', 'value': 0}], 'summary.json', 'repo1')
    gs.save_data([], 'summary.json', 'repo2')
    revs = gs.repo_activity()

    assert gs.load_data('activity.json', 'repo1') == data1
    assert gs.load_data('activity.json', 'repo2') == data2
    assert gs.load_data('summary.json', 'repo1') == [{'key': 'authors',
                                                      'value': 1}]
    assert gs.load_data('summary.json', 'repo2') == []
    assert revs == {'repo1': ['r1', 'r2'], 'repo2': ['r3']}

    collectors.activity = _tmp


def test_repo_lines(stat, mocker):
    _tmp = collectors.count_lines

    collectors.count_lines = mocker.Mock()
    collectors.count_lines.side_effect = [
        {'repo': 'repo1', 'data': 'data1'},
        {'repo': 'repo2', 'data': 'data2'},
    ]

    gs = stat['cls']
    gs.repos = ['repo1', 'repo2']
    gs.repo_lines()

    assert gs.load_data('lines.json', 'repo1') == 'data1'
    assert gs.load_data('lines.json', 'repo2') == 'data2'

    collectors.count_lines = _tmp


def test_repo_branches(stat, mocker):
    _tmp1 = collectors.get_branches
    _tmp2 = collectors.get_timestamp

    collectors.get_branches = mocker.Mock()
    collectors.get_branches.side_effect = [
        {'repo': 'repo1', 'data': 'data1', 'branches': []},
        {'repo': 'repo2', 'data': 'data2', 'branches': ['b1']},
    ]

    collectors.get_timestamp = mocker.Mock()
    collectors.get_timestamp.side_effect = [
        {'timestamp': 123456},
    ]

    gs = stat['cls']
    gs.repos = ['repo1', 'repo2']
    gs.repo_branches()

    assert gs.load_data('branches.json', 'repo1') == []
    assert gs.load_data('branches.json', 'repo2') == [{'timestamp': 123456}]

    collectors.get_branches = _tmp1
    collectors.get_timestamp = _tmp2


def test_repo_file_history(stat, mocker):
    _tmp = collectors.num_files

    collectors.num_files = mocker.Mock()
    collectors.num_files.side_effect = [
        {'data': 'data1'},
        {'data': 'data2'},
    ]

    revs = {
        'repo1': {'revision': 'r1'},
        'repo2': {'revision': 'r2'},
    }

    gs = stat['cls']
    gs.repos = ['repo1', 'repo2']
    gs.repo_files_history(revs)

    assert gs.load_data('files-history.json', 'repo1') == {'data': 'data1'}
    assert gs.load_data('files-history.json', 'repo2') == {'data': 'data2'}

    collectors.num_files = _tmp


def test_repo_file_history_cache(stat, mocker):
    _tmp = collectors.num_files

    collectors.num_files = mocker.Mock()
    collectors.num_files.side_effect = [
        {'data': 'data'},
    ]

    revs = {
        'repo1': [{'revision': 'r1'}],
        'repo2': [{'revision': 'r2'}],
    }

    fname = 'files-history.json'
    gs = stat['cls']

    gs.repos = ['repo1', 'repo2']
    gs.save_data({'r1': 'old_data'}, fname, 'repo1')

    gs.repo_files_history(revs)

    assert gs.load_data(fname, 'repo1') == {'r1': 'old_data'}
    assert gs.load_data(fname, 'repo2') == {'data': 'data'}

    collectors.num_files = _tmp


def test_repo_tags(stat, mocker):
    _tmp1 = collectors.get_tags
    _tmp2 = collectors.get_timestamp
    _tmp3 = utils.run_git

    collectors.get_tags = mocker.Mock()
    collectors.get_tags.side_effect = [
        {'repo': 'repo1', 'tags': []},
        {'repo': 'repo2', 'tags': [{'revision': 't1'}, {'revision': 't2'}]}
    ]
    collectors.get_timestamp = mocker.Mock()
    collectors.get_timestamp.side_effect = [
        {'revision': 't1', 'timestamp': 123456},
        {'revision': 't2', 'timestamp': 234567},
    ]
    utils.run_git = mocker.Mock()
    utils.run_git.side_effect = [
        '15\tauthor1\n20\tauthor3',
        '5\tauthor1\n10\tauthor2',
    ]

    fname = 'tags.json'
    gs = stat['cls']

    gs.repos = ['repo1', 'repo2']

    gs.repo_tags()

    assert gs.load_data(fname, 'repo1') == []
    assert gs.load_data(fname, 'repo2') == [
        {
            'authors': [
                {'author': 'author1', 'commits': 15},
                {'author': 'author3', 'commits': 20},
            ],
            'revision': 't2',
            'timestamp': 234567,
        },
        {
            'authors': [
                {'author': 'author1', 'commits': 5},
                {'author': 'author2', 'commits': 10},
            ],
            'revision': 't1',
            'timestamp': 123456,
        },
    ]

    collectors.get_tags = _tmp1
    collectors.get_timestamp = _tmp2
    utils.run_git = _tmp3


def test_repo_blame(stat, mocker):
    _tmp1 = collectors.get_blame
    _tmp2 = utils.run_git

    collectors.get_blame = mocker.Mock()
    collectors.get_blame.side_effect = [
        {'authors': {'author1': 10, 'author2': 20}, 'file': 'f1'},
        {'authors': {}, 'file': 'f2'},
    ]
    utils.run_git = mocker.Mock()
    utils.run_git.side_effect = [
        '10644 blob rev1 f1',
        '10644 blob rev2 f2',
    ]

    gs = stat['cls']

    gs.repos = ['repo1', 'repo2']

    gs.repo_blame()

    assert gs.load_data('files-authors.json', 'repo1') == {
        'f1': {
            'authors': {'author1': 10, 'author2': 20},
            'revision': 'rev1',
        },
    }
    assert gs.load_data('files-authors.json', 'repo2') == {
        'f2': {'authors': {}, 'revision': 'rev2'},
    }

    assert gs.load_data('authors.json', 'repo1') == {
        'files': {'author1': 1, 'author2': 1},
        'lines': {'author1': 10, 'author2': 20},
    }
    assert gs.load_data('authors.json', 'repo2') == {'files': {}, 'lines': {}}

    collectors.get_tags = _tmp1
    utils.run_git = _tmp2


def test_repo_blame_with_cache(stat, mocker):
    _tmp1 = collectors.get_blame
    _tmp2 = utils.run_git

    collectors.get_blame = mocker.Mock()
    collectors.get_blame.side_effect = [
        {'authors': {'author1': 10, 'author2': 20}, 'file': 'f1'},
    ]
    utils.run_git = mocker.Mock()
    utils.run_git.side_effect = [
        """10644 blob rev1 f1
        '10644 blob rev2 f2"""
    ]

    cache = {
        'f2': {
            'authors': {'author1': 30, 'author3': 10},
            'revision': 'rev2',
        },
    }

    gs = stat['cls']
    gs.save_data(cache, 'files-authors.json', 'repo1')

    gs.repos = ['repo1']

    gs.repo_blame()

    assert gs.load_data('files-authors.json', 'repo1') == {
        'f1': {
            'authors': {'author1': 10, 'author2': 20},
            'revision': 'rev1',
        },
        'f2': {
            'authors': {'author1': 30, 'author3': 10},
            'revision': 'rev2',
        },
    }

    assert gs.load_data('authors.json', 'repo1') == {
        'files': {'author1': 2, 'author2': 1, 'author3': 1},
        'lines': {'author1': 40, 'author2': 20, 'author3': 10},
    }

    collectors.get_tags = _tmp1
    utils.run_git = _tmp2
