import configparser
import os
import tempfile

from . import config, utils


def test_default_conf():
    conf = config.Config()
    assert conf.force is False
    assert conf.config_path == os.path.join(utils.PROJECT_DIR, 'config.ini')
    c = conf.config
    assert isinstance(c, configparser.ConfigParser)
    assert conf.config is c


def test_conf_accessor():
    with tempfile.NamedTemporaryFile() as fh:
        fh.write(b"""
        [section]
        key = value
        """)
        fh.flush()
        conf = config.Config(config_path=fh.name)
        assert dict(conf.section) == {'key': 'value'}


def test_repositories():
    with tempfile.NamedTemporaryFile() as fh:
        fh.write(b"""
        [REPOSITORIES]
        example =
            clone: ssh://example.com/clone
            web: http://example.com/code
            site: http://example.com/
        """)
        fh.flush()
        conf = config.Config(config_path=fh.name)
        assert conf.repositories() == {
            'example': {
                'clone': 'ssh://example.com/clone',
                'web': 'http://example.com/code',
                'site': 'http://example.com/',
            },
        }
