import ast
import json
import os.path

from packaging.utils import canonicalize_name

from all_repos_depends.errors import DependsError
from all_repos_depends.lang import js
from all_repos_depends.lang import python
from all_repos_depends.types import Package


class FindsPackageName(ast.NodeVisitor):
    name = None

    def visit_Call(self, node):
        if python.node_is_setup_call(node):
            for kwd in node.keywords:
                if kwd.arg == 'name' and isinstance(kwd.value, ast.Str):
                    self.name = kwd.value.s

        self.generic_visit(node)


def setup_py():
    if not os.path.exists('setup.py'):
        return None

    visitor = FindsPackageName()
    visitor.visit(python.load_setup_py_ast())
    if visitor.name:
        return Package(
            python.NAME,
            key=canonicalize_name(visitor.name),
            name=python.to_name(visitor.name),
        )
    else:
        raise DependsError('Had setup.py but could not determine name')


def package_json():
    if not os.path.exists('package.json'):
        return None

    with open('package.json') as f:
        contents = json.load(f)
    return Package(js.NAME, contents['name'], contents['name'])
