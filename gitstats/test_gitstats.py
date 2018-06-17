import json
import os
from datetime import datetime
from tempfile import NamedTemporaryFile as tf, TemporaryDirectory as td

import pytest

from . import gitstats, config


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

        cfg = config.Config(config_path=f.name)
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
