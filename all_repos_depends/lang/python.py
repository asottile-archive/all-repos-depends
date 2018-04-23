import ast
import os.path

from packaging.requirements import InvalidRequirement
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

from all_repos_depends.errors import DependsError
from all_repos_depends.types import Depends

NAME = 'python'


def to_name(s):
    return s.lower().replace('_', '-')


def load_setup_py_ast():
    with open('setup.py', 'rb') as f:
        try:
            return ast.parse(f.read(), filename='setup.py')
        except SyntaxError:
            raise DependsError('Had setup.py but could not be parsed')


def node_is_setup_call(node):
    return (
        # setup(
        (isinstance(node.func, ast.Name) and node.func.id == 'setup') or
        # setuptools.setup(
        (
            isinstance(node.func, ast.Attribute) and
            isinstance(node.func.value, ast.Name) and
            node.func.value.id == 'setuptools' and
            node.func.attr == 'setup'
        )
    )


def to_depends(relationship, requirement_s):
    try:
        req = Requirement(requirement_s)
    except InvalidRequirement:
        return Depends(relationship, NAME, requirement_s, ' (unable to parse)')

    spec_parts = []
    if req.extras:
        spec_parts.append('[{}]'.format(','.join(sorted(req.extras))))
    if req.specifier:
        spec_parts.append(str(req.specifier))
    if req.marker:
        spec_parts.append(f';{req.marker}')
    spec = ''.join(spec_parts)

    return Depends(relationship, NAME, canonicalize_name(req.name), spec)


def from_reqs_file(relationship, filename):
    with open(filename) as f:
        for line in f:
            line, _, _ = line.partition('#')
            line = line.strip()

            # local editable paths aren't all that interesting
            if line.startswith('-e '):
                _, _, path = line.partition(' ')
                path = os.path.join(os.path.dirname(filename), path)
                if os.path.exists(path):
                    continue

            if line:
                yield to_depends(relationship, line)
