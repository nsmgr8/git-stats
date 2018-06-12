import json
import subprocess
from . import collectors


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
    collectors.clone('/tmp', 'foo', 'bar')
    assert_subprocess_run('git clone bar foo')


def test_clone_on_exception(mocker):
    run = mocker.patch('subprocess.run')
    run.side_effect = Exception('failed')
    collectors.clone('/tmp', 'foo', 'bar')
    assert_subprocess_run('git clone bar foo')


def test_get_timestamp(mocker):
    run = mocker.patch('subprocess.run')
    run.return_value = CompletedProcessMock('123456')
    result = {'timestamp': 123456, 'revision': 'bar'}
    assert collectors.get_timestamp('/', 'tmp', 'bar') == result
    assert_subprocess_run('git log --pretty=format:"%at" -n 1 bar')


def test_get_blame(mocker):
    run = mocker.patch('subprocess.run')
    run.return_value = CompletedProcessMock(blame_text)
    result = {'authors': {'M Nasimul Haque': 2}, 'file': 'file.txt'}
    assert collectors.get_blame('/', 'tmp', False, 'file.txt') == result
    assert_subprocess_run('git blame --line-porcelain  -w file.txt')


def test_get_blame_detect_move(mocker):
    run = mocker.patch('subprocess.run')
    run.return_value = CompletedProcessMock(blame_text)
    result = {'authors': {'M Nasimul Haque': 2}, 'file': 'file.txt'}
    assert collectors.get_blame('/', 'tmp', True, 'file.txt') == result
    assert_subprocess_run('git blame --line-porcelain -C -C -C -M -w file.txt')


def test_get_blame_on_exception(mocker):
    run = mocker.patch('subprocess.run')
    run.side_effect = Exception('failed')
    result = {'authors': {}, 'file': 'file.txt'}
    assert collectors.get_blame('/', 'tmp', False, 'file.txt') == result
    assert_subprocess_run('git blame --line-porcelain  -w file.txt')


def test_get_branches(mocker):
    run = mocker.patch('subprocess.run')
    run.return_value = CompletedProcessMock('b1\nb2\nb3 HEAD')
    result = {'branches': ['b1', 'b2'], 'repo': 'tmp'}
    assert collectors.get_branches('/', 'tmp') == result
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
    assert collectors.get_tags('/', 'tmp') == result
    assert_subprocess_run('git show-ref --tags')


def test_get_tags_on_exception(mocker):
    run = mocker.patch('subprocess.run')
    run.side_effect = Exception('failed')
    result = {'repo': 'tmp', 'tags': []}
    assert collectors.get_tags('/', 'tmp') == result
    assert_subprocess_run('git show-ref --tags')


def test_num_files(mocker):
    run = mocker.patch('subprocess.run')
    run.return_value = CompletedProcessMock('f1\nf2')
    result = {'12345': {'files': 2, 'timestamp': 12345}}
    revision = {'revision': '12345', 'timestamp': 12345}
    assert collectors.num_files('/', 'tmp', revision) == result
    assert_subprocess_run('git ls-tree -r --name-only 12345')


def test_count_lines(mocker):
    run = mocker.patch('subprocess.run')
    run.return_value = CompletedProcessMock('{"lines": "data from cloc"}')
    result = {'data': {'lines': {'lines': 'data from cloc'}}, 'repo': 'tmp'}
    assert collectors.count_lines('/', 'tmp') == result
    assert_subprocess_run('cloc --vcs git --json')


def test_count_lines_on_exception(mocker):
    run = mocker.patch('subprocess.run')
    run.side_effect = Exception('failed')
    result = {'data': {'lines': []}, 'repo': 'tmp'}
    assert collectors.count_lines('/', 'tmp') == result
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
    assert json.loads(json.dumps(collectors.activity('/', 'tmp'))) == result
    assert_subprocess_run('git log --shortstat --pretty=format:"%at %T %aN" HEAD')


def test_summary(mocker):
    run = mocker.patch('subprocess.run')
    run.side_effect = [
        # empty sha generator
        CompletedProcessMock('1234'),
        # diff --shortstat
        CompletedProcessMock(' 98 files changed, 10564 insertions(+)'),
        # shortlog -s
        CompletedProcessMock('    93  M Nasimul Haque'),
        # rev-list --count HEAD
        CompletedProcessMock('93'),
        # branch -r
        CompletedProcessMock('origin/master'),
        # log --reverse %at
        CompletedProcessMock('1527621944\n1527761990\n1527763244'),
        # log %at -n1
        CompletedProcessMock('1528755935'),
        # show-ref --tags
        CompletedProcessMock('refs/tags/v1'),
    ]
    result = {
        'data': [
            {'key': 'files', 'value': '98'},
            {'key': 'lines', 'notes': 'includes empty lines', 'value': '10564'},
            {'key': 'authors', 'value': 1},
            {'key': 'commits', 'notes': 'master only', 'value': '93'},
            {'key': 'branches', 'value': 1},
            {'key': 'tags', 'value': 1},
            {'key': 'age', 'notes': 'active days since creation', 'value': 14}],
        'repo': 'tmp',
    }
    assert collectors.summary('/', 'tmp') == result


def test_summary_on_exception(mocker):
    run = mocker.patch('subprocess.run')
    run.side_effect = [
        # empty sha generator
        CompletedProcessMock('1234'),
        # diff --shortstat
        CompletedProcessMock(' 98 files changed, 10564 insertions(+)'),
        # shortlog -s
        CompletedProcessMock('    93  M Nasimul Haque'),
        # rev-list --count HEAD
        CompletedProcessMock('93'),
        # branch -r
        CompletedProcessMock('origin/master'),
        # log --reverse %at
        CompletedProcessMock('1527621944\n1527761990\n1527763244'),
        # log %at -n1
        CompletedProcessMock('1528755935'),
        # show-ref --tags
        Exception('refs/tags/v1'),
    ]
    result = {
        'data': [
            {'key': 'files', 'value': '98'},
            {'key': 'lines', 'notes': 'includes empty lines', 'value': '10564'},
            {'key': 'authors', 'value': 1},
            {'key': 'commits', 'notes': 'master only', 'value': '93'},
            {'key': 'branches', 'value': 1},
            {'key': 'tags', 'value': 0},
            {'key': 'age', 'notes': 'active days since creation', 'value': 14}],
        'repo': 'tmp',
    }
    assert collectors.summary('/', 'tmp') == result


def test_update_repo(mocker):
    run = mocker.patch('subprocess.run')
    run.side_effect = [
        # clone
        CompletedProcessMock(''),
        # pull --tags
        CompletedProcessMock(''),
        # log --pretty=format:"%H %at %aN" -n1
        CompletedProcessMock('head 23456 author'),
        # log --reverse --pretty=format:"%at"
        CompletedProcessMock('12345'),
    ]
    result = {
        'HEAD': 'head',
        'author': 'author',
        'date': 23456,
        'name': 'tmp',
        'start_date': 12345,
    }
    assert collectors.update_repo('/', ['tmp', 'https://example.com']) == result


def test_update_repo_on_exception(mocker):
    run = mocker.patch('subprocess.run')
    run.side_effect = Exception('')
    assert collectors.update_repo('/', ['tmp', 'https://example.com']) == {}
