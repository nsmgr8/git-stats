import configparser
import os
import tempfile

from . import config, utils


def test_default_conf():
    conf = config.Config()
    assert conf.force is False
    assert conf.config_path == os.path.join(utils.PROJECT_DIR, 'config.ini')
    assert isinstance(conf.config, configparser.ConfigParser)


def test_conf_accessor():
    with tempfile.NamedTemporaryFile() as fh:
        fh.write(b"""
        [section]
        key = value
        """)
        fh.flush()
        conf = config.Config(config_path=fh.name)
        assert dict(conf.section) == {'key': 'value'}
