from . import __main__ as main


def test_parse_command_args():
    default_args = {'force': False, 'verbose': False, 'config_path': None}

    args = main.parse_command_args([])
    assert vars(args) == default_args

    args = main.parse_command_args(['-v'])
    assert vars(args) == {**default_args, 'verbose': True}

    args = main.parse_command_args(['-f'])
    assert vars(args) == {**default_args, 'force': True}

    args = main.parse_command_args(['-c', '/tmp/conf.ini'])
    assert vars(args) == {**default_args, 'config_path': '/tmp/conf.ini'}

    args = main.parse_command_args(['-v', '-f'])
    assert vars(args) == {**default_args, 'force': True, 'verbose': True}
