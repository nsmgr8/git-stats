import subprocess
from . import gitstats


class CompletedProcessMock:
    def __init__(self, stdout='', stderr=''):
        self.stdout = stdout
        self.stderr = stderr


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
