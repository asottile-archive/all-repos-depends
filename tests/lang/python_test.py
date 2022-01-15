from __future__ import annotations

import pytest

from all_repos_depends.lang import python
from all_repos_depends.types import Depends


@pytest.mark.parametrize(
    ('s', 'expected'),
    (
        ('pre-commit', 'pre-commit'),
        ('pre_commit', 'pre-commit'),
        ('PRE_COMMIT', 'pre-commit'),
    ),
)
def test_to_name(s, expected):
    assert python.to_name(s) == expected


@pytest.mark.parametrize(
    ('s', 'expected'),
    (
        ('pre-commit', Depends('X', 'python', 'pre-commit', '')),
        ('six==1.10', Depends('X', 'python', 'six', '==1.10')),
        ('foo[bar,baz]', Depends('X', 'python', 'foo', '[bar,baz]')),
        (
            'typing;python_version=="2.7"',
            Depends('X', 'python', 'typing', ';python_version == "2.7"'),
        ),
    ),
)
def test_to_depends(s, expected):
    assert python.to_depends('X', s) == expected


def test_from_reqs_file_comments(tmpdir):
    f = tmpdir.join('reqs.txt')
    f.write(
        '\n'
        '# hello world\n'
        'six  # more comments\n',
    )
    expected = (Depends('X', 'python', 'six', ''),)
    assert tuple(python.from_reqs_file('X', f)) == expected


def test_from_reqs_file_ignores_local_paths(tmpdir):
    f = tmpdir.join('reqs.txt')
    f.write('-e foo\n-e .\nsix\n')
    tmpdir.join('foo').ensure_dir()
    expected = (Depends('X', 'python', 'six', ''),)
    assert tuple(python.from_reqs_file('X', f)) == expected


def test_fomr_reqs_file_editable_git(tmpdir):
    f = tmpdir.join('reqs.txt')
    f.write('-e git+https://github.com/asottile/cfgv')
    expected = (
        Depends(
            'X', 'python',
            '-e git+https://github.com/asottile/cfgv', ' (unable to parse)',
        ),
    )
    assert tuple(python.from_reqs_file('X', f)) == expected
