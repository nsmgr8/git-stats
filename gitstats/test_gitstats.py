import json
import subprocess
from . import gitstats


class CompletedProcessMock:
    def __init__(self, stdout='', stderr=''):
        self.stdout = stdout
        self.stderr = stderr


blame_text = """\
aacd7f517fb0312ec73f882a345d50c6e8512405 1 1 1
author M Nasimul Haque
...
filename file.txt
	line one
4cbb5a68de251bf42ecfc2b127fd2596c0d17d3f 1 2 1
author M Nasimul Haque
...
filename file.txt
	line two
"""     # flake8: noqa

shortlog_text = """\
1528753992 dcc3c393 M Nasimul Haque
 1 file changed, 1 insertion(+), 1 deletion(-)

1528753813 a36e16b3 M Nasimul Haque
 1 file changed, 3 insertions(+)
"""


def assert_subprocess_run(cmd):
    assert subprocess.run.call_count == 1
    subprocess.run.assert_any_call(
        f'nice -n 20 {cmd}', cwd='/tmp', check=True, shell=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
    )


def test_clone(mocker):
    mocker.patch('subprocess.run')
    gitstats.clone('/tmp', 'foo', 'bar')
    assert_subprocess_run('git clone bar foo')


def test_get_timestamp(mocker):
    run = mocker.patch('subprocess.run')
    run.return_value = CompletedProcessMock('123456')
    result = {'timestamp': 123456, 'revision': 'bar'}
    assert gitstats.get_timestamp('/', 'tmp', 'bar') == result
    assert_subprocess_run('git log --pretty=format:"%at" -n 1 bar')


def test_get_blame(mocker):
    run = mocker.patch('subprocess.run')
    run.return_value = CompletedProcessMock(blame_text)
    result = {'authors': {'M Nasimul Haque': 2}, 'file': 'file.txt'}
    assert gitstats.get_blame('/', 'tmp', False, 'file.txt') == result
    assert_subprocess_run('git blame --line-porcelain  -w file.txt')


def test_get_blame_detect_move(mocker):
    run = mocker.patch('subprocess.run')
    run.return_value = CompletedProcessMock(blame_text)
    result = {'authors': {'M Nasimul Haque': 2}, 'file': 'file.txt'}
    assert gitstats.get_blame('/', 'tmp', True, 'file.txt') == result
    assert_subprocess_run('git blame --line-porcelain -C -C -C -M -w file.txt')


def test_get_blame_on_exception(mocker):
    run = mocker.patch('subprocess.run')
    run.side_effect = Exception('failed')
    result = {'authors': {}, 'file': 'file.txt'}
    assert gitstats.get_blame('/', 'tmp', False, 'file.txt') == result
    assert_subprocess_run('git blame --line-porcelain  -w file.txt')


def test_get_branches(mocker):
    run = mocker.patch('subprocess.run')
    run.return_value = CompletedProcessMock('b1\nb2')
    result = {'branches': ['b1', 'b2'], 'repo': 'tmp'}
    assert gitstats.get_branches('/', 'tmp') == result
    assert_subprocess_run('git branch -r')


def test_get_tags(mocker):
    run = mocker.patch('subprocess.run')
    run.return_value = CompletedProcessMock('123 b1\n456 b2')
    result = {
        'tags': [
            {'revision': '123', 'tag': 'b1'},
            {'revision': '456', 'tag': 'b2'},
        ],
        'repo': 'tmp',
    }
    assert gitstats.get_tags('/', 'tmp') == result
    assert_subprocess_run('git show-ref --tags')


def test_get_tags_on_exception(mocker):
    run = mocker.patch('subprocess.run')
    run.side_effect = Exception('failed')
    result = {'repo': 'tmp', 'tags': []}
    assert gitstats.get_tags('/', 'tmp') == result
    assert_subprocess_run('git show-ref --tags')


def test_num_files(mocker):
    run = mocker.patch('subprocess.run')
    run.return_value = CompletedProcessMock('f1\nf2')
    result = {'12345': {'files': 2, 'timestamp': 12345}}
    revision = {'revision': '12345', 'timestamp': 12345}
    assert gitstats.num_files('/', 'tmp', revision) == result
    assert_subprocess_run('git ls-tree -r --name-only 12345')


def test_count_lines(mocker):
    run = mocker.patch('subprocess.run')
    run.return_value = CompletedProcessMock('{"lines": "data from cloc"}')
    result = {'data': {'lines': {'lines': 'data from cloc'}}, 'repo': 'tmp'}
    assert gitstats.count_lines('/', 'tmp') == result
    assert_subprocess_run('cloc --vcs git --json')


def test_activity(mocker):
    run = mocker.patch('subprocess.run')
    run.return_value = CompletedProcessMock(shortlog_text)
    result = {
        'data': {
            'authors_age': {
                'M Nasimul Haque': {
                    'days': 1,
                    'first_commit': 1528753813,
                    'last_commit': 1528753992,
                },
            },
            'by_authors': {
                'M Nasimul Haque': {
                    'at_hour': {
                        'commits': {'22': 2},
                        'deletions': {'22': 1},
                        'insertions': {'22': 4},
                    },
                    'daily': {
                        'commits': {'2018-06-11': 2},
                        'deletions': {'2018-06-11': 1},
                        'insertions': {'2018-06-11': 4},
                    },
                    'monthly': {
                        'commits': {'2018-06': 2},
                        'deletions': {'2018-06': 1},
                        'insertions': {'2018-06': 4},
                    },
                    'weekly': {
                        'commits': {'2018-24': 2},
                        'deletions': {'2018-24': 1},
                        'insertions': {'2018-24': 4},
                    },
                    'yearly': {
                        'commits': {'2018': 2},
                        'deletions': {'2018': 1},
                        'insertions': {'2018': 4},
                    },
                }
            },
            'by_time': {
                'at_hour': {
                    'commits': {'22': 2},
                    'deletions': {'22': 1},
                    'insertions': {'22': 4},
                },
                'daily': {
                    'commits': {'2018-06-11': 2},
                    'deletions': {'2018-06-11': 1},
                    'insertions': {'2018-06-11': 4},
                },
                'monthly': {
                    'commits': {'2018-06': 2},
                    'deletions': {'2018-06': 1},
                    'insertions': {'2018-06': 4},
                },
                'weekly': {
                    'commits': {'2018-24': 2},
                    'deletions': {'2018-24': 1},
                    'insertions': {'2018-24': 4},
                },
                'yearly': {
                    'commits': {'2018': 2},
                    'deletions': {'2018': 1},
                    'insertions': {'2018': 4},
                },
            },
            'hour_of_week': {'0': {'22': 2}},
        },
        'repo': 'tmp',
        'revisions': [
            {'revision': 'dcc3c393', 'timestamp': 1528753992},
            {'revision': 'a36e16b3', 'timestamp': 1528753813},
        ],
    }
    assert json.loads(json.dumps(gitstats.activity('/', 'tmp'))) == result
    assert_subprocess_run('git log --shortstat --pretty=format:"%at %T %aN" HEAD')
