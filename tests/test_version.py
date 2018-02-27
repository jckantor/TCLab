import pytest

import re
import tclab


def test_version_type():
    """Test that version is a string."""
    assert isinstance(tclab.__version__, str)


def test_version_file():
    """Test code used in conf.py for recovering version."""
    exec(open('./tclab/version.py').read())


def test_version_conf():
    """Test code used in conf.py for recovering version."""
    version = '.'.join(tclab.__version__.split('.')[0:2])


def test_version_regex():
    """Regular expression match for version number with optional dev at end."""
    assert re.match('^(\d+\.)(\d+\.)(\d+)(dev)?$', tclab.__version__)
