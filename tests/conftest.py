from __future__ import annotations

import contextlib
import json
import subprocess

import pytest
from all_repos import clone

from all_repos_depends import generate


@contextlib.contextmanager
def _git_dir(p):
    subprocess.check_call(('git', 'init', p))
    yield p
    subprocess.check_call(('git', '-C', p, 'add', '--all', ':/'))
    subprocess.check_call(('git', '-C', p, 'commit', '-m', 'commit!'))


@pytest.fixture(scope='session')
def generated(tmpdir_factory):
    root = tmpdir_factory.mktemp('generated')

    repodir = root.join('repos')

    with _git_dir(repodir.join('1')) as r1:
        r1.join('setup.py').write(
            'from setuptools import setup\n'
            'setup(name="pkg1", install_requires=["pkg2", "six"])\n',
        )

    with _git_dir(repodir.join('2')) as r2:
        r2.join('setup.py').write(
            'from setuptools import setup\n'
            'setup(name="pkg2")\n',
        )
        r2.join('requirements-dev.txt').write('pytest\npre-commit\n')

    # intentional error
    with _git_dir(repodir.join('3')) as r3:
        r3.join('setup.py').write('from setuptools import setup; setup()')

    # intentionally empty
    with _git_dir(repodir.join('4')) as r4:
        r4.join('f').ensure()

    # also provides a pkg2, but in javascript
    with _git_dir(repodir.join('5')) as r5:
        r5.join('package.json').write('{"name": "pkg2"}')

    repos_json = repodir.join('repos.json')
    repos_json.write(
        json.dumps({
            'r1': str(r1), 'r2': str(r2), 'r3': str(r3), 'r4': str(r4),
            'r5': str(r5),
        }),
    )

    all_repos = root.join('all_repos').ensure_dir()
    all_repos_cfg = all_repos.join('all-repos.json')
    all_repos_cfg.write(
        json.dumps({
            'output_dir': 'output',
            'source': 'all_repos.source.json_file',
            'source_settings': {'filename': str(repos_json)},
            'push': 'all_repos.push.merge_to_master',
            'push_settings': {},
        }),
    )
    all_repos_cfg.chmod(0o600)

    assert not clone.main(('--config-filename', str(all_repos_cfg)))

    all_repos_depends = root.join('all_repos_depends').ensure_dir()
    all_repos_depends_cfg = all_repos_depends.join('all-repos-depends.json')
    all_repos_depends_cfg.write(
        json.dumps({
            'all_repos_config': str(all_repos_cfg),
            'get_packages': [
                'all_repos_depends.packages.setup_py',
                'all_repos_depends.packages.package_json',
            ],
            'get_depends': [
                'all_repos_depends.depends.setup_py',
                'all_repos_depends.depends.requirements_tools',
            ],
        }),
    )
    database_path = all_repos_depends.join('database.db')

    assert not generate.main((
        '--config-filename', str(all_repos_depends_cfg),
        '--database', str(database_path),
    ))

    return str(database_path)
