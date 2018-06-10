import json
import os
import shutil
import subprocess
import uuid

from gitstats import utils


def test_PROJECT_DIR():
    here = os.path.dirname(__file__)
    assert utils.PROJECT_DIR == os.path.dirname(here)


def test_run():
    assert isinstance(utils.run('true'), subprocess.CompletedProcess)


def test_run_git():
    assert utils.run_git('.', '.', 'status')


def test_empty_git_sha():
    sha = '4b825dc642cb6eb9a060e54bf8d69288fbee4904'
    assert utils.empty_git_sha('.', '.') == sha


def test_save_json():
    data = {'test': 'data'}
    root = '/tmp'
    fname = str(uuid.uuid4())
    folders = str(uuid.uuid4()).split('-')

    utils.save_json(data, root, fname, folders)

    fpath = os.path.join(root, *folders, fname)
    with open(fpath) as fh:
        content = json.loads(fh.read())

    assert data == content

    shutil.rmtree(os.path.join(root, folders[0]))
