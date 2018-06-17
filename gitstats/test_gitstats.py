import os
from tempfile import NamedTemporaryFile, TemporaryDirectory

import pytest

from . import gitstats, config


@pytest.fixture()
def stat():
    with TemporaryDirectory() as d, NamedTemporaryFile() as f:
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
        print(list(cfg.GLOBAL.items()))

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
