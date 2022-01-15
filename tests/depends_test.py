from __future__ import annotations

import pytest

from all_repos_depends.depends import requirements_tools
from all_repos_depends.depends import setup_py
from all_repos_depends.errors import DependsError
from all_repos_depends.types import Depends


@pytest.mark.parametrize('fn', (requirements_tools, setup_py))
def test_empty_repo_returns_empty_tuple(tmpdir, fn):
    with tmpdir.as_cwd():
        assert fn() == ()


def test_setup_py_trivial(tmpdir):
    with tmpdir.as_cwd():
        tmpdir.join('setup.py').write(
            'from setuptools import setup\n'
            'setup(name="mypkg")\n',
        )
        assert setup_py() == ()


def test_setup_py_has_install_dependencies(tmpdir):
    with tmpdir.as_cwd():
        tmpdir.join('setup.py').write(
            'from setuptools import setup, find_packages\n'
            'setup(\n'
            '    name="mypkg",\n'
            '    install_requires=["six>=1.10.0", "pre-commit"],\n'
            '    packages=find_packages(),\n'
            ')\n',
        )
        assert setup_py() == (
            Depends('DEPENDS', 'python', 'six', '>=1.10.0'),
            Depends('DEPENDS', 'python', 'pre-commit', ''),
        )


def test_setup_py_error_when_not_static(tmpdir):
    with tmpdir.as_cwd():
        tmpdir.join('setup.py').write(
            'from setuptools import setup\n'
            'from mypkg import SIXDEP\n'
            'setup(\n'
            '    name="mypkg",\n'
            '    install_requires=[SIXDEP],\n'
            ')\n',
        )
        with pytest.raises(DependsError) as excinfo:
            setup_py()
        msg, = excinfo.value.args
        assert msg == (
            'Had setup.py with install_requires but it was not a list of '
            'strings'
        )


def test_requirements_tools_all_provided(tmpdir):
    with tmpdir.as_cwd():
        tmpdir.join('requirements-minimal.txt').write('six')
        tmpdir.join('requirements.txt').write('six==1.11')
        tmpdir.join('requirements-dev-minimal.txt').write('mccabe')
        tmpdir.join('requirements-dev.txt').write('mccabe==0.6.1')
        assert requirements_tools() == (
            Depends('DEPENDS', 'python', 'six', ''),
            Depends('REQUIRES', 'python', 'six', '==1.11'),
            Depends('DEPENDS_DEV', 'python', 'mccabe', ''),
            Depends('REQUIRES_DEV', 'python', 'mccabe', '==0.6.1'),
        )


def test_requirements_tools_just_reqs(tmpdir):
    with tmpdir.as_cwd():
        tmpdir.join('requirements.txt').write('six')
        tmpdir.join('requirements-dev.txt').write('pre-commit\npytest\n')
        assert requirements_tools() == (
            Depends('REQUIRES', 'python', 'six', ''),
            Depends('DEPENDS_DEV', 'python', 'pre-commit', ''),
            Depends('DEPENDS_DEV', 'python', 'pytest', ''),
        )
