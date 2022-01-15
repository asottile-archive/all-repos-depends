from __future__ import annotations

import pytest

from all_repos_depends.errors import DependsError
from all_repos_depends.packages import package_json
from all_repos_depends.packages import setup_py
from all_repos_depends.types import Package


@pytest.mark.parametrize('fn', (package_json, setup_py))
def test_empty_repo_returns_none(tmpdir, fn):
    with tmpdir.as_cwd():
        assert fn() is None


def test_package_json(tmpdir):
    with tmpdir.as_cwd():
        tmpdir.join('package.json').write('{"name": "mypkg", "version": "1"}')
        assert package_json() == Package('js', 'mypkg', 'mypkg')


def test_setup_py_unparseable(tmpdir):
    with tmpdir.as_cwd():
        tmpdir.join('setup.py').write('setup(')
        with pytest.raises(DependsError) as excinfo:
            setup_py()
        msg, = excinfo.value.args
        assert msg == 'Had setup.py but could not be parsed'


def test_setup_py_parseable_but_no_name_detected(tmpdir):
    with tmpdir.as_cwd():
        tmpdir.join('setup.py').write('')
        with pytest.raises(DependsError) as excinfo:
            setup_py()
        msg, = excinfo.value.args
        assert msg == 'Had setup.py but could not determine name'


def test_setup_py_finds_name_and_normalizes(tmpdir):
    with tmpdir.as_cwd():
        tmpdir.join('setup.py').write(
            'from setuptools import setup, find_packages\n'
            'setup(name="aspy.YAML", packages=find_packages())\n',
        )
        assert setup_py() == Package('python', 'aspy-yaml', 'aspy.yaml')


def test_setup_py_setuptools_setup(tmpdir):
    with tmpdir.as_cwd():
        tmpdir.join('setup.py').write(
            'import setuptools\n'
            'setuptools.setup(name="mypkg")\n',
        )
        assert setup_py() == Package('python', 'mypkg', 'mypkg')
