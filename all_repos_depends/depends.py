from __future__ import annotations

import ast
import os.path

from all_repos_depends.errors import DependsError
from all_repos_depends.lang import python
from all_repos_depends.types import Depends


class FindsInstallRequires(ast.NodeVisitor):
    def __init__(self) -> None:
        self.requires: list[Depends] = []

    def visit_Call(self, node: ast.Call) -> None:
        if python.node_is_setup_call(node):
            for kwd in node.keywords:
                if (
                        kwd.arg == 'install_requires' and
                        isinstance(kwd.value, ast.List)
                ):
                    if all(isinstance(e, ast.Str) for e in kwd.value.elts):
                        for elt in kwd.value.elts:
                            assert isinstance(elt, ast.Str)
                            req = python.to_depends('DEPENDS', elt.s)
                            self.requires.append(req)
                    else:
                        raise DependsError(
                            'Had setup.py with install_requires but it was '
                            'not a list of strings',
                        )

        self.generic_visit(node)


def setup_py() -> tuple[Depends, ...]:
    if not os.path.exists('setup.py'):
        return ()

    visitor = FindsInstallRequires()
    visitor.visit(python.load_setup_py_ast())
    return tuple(visitor.requires)


def requirements_tools() -> tuple[Depends, ...]:
    reqs_minimal = 'requirements-minimal.txt'
    reqs = 'requirements.txt'
    reqs_dev_minimal = 'requirements-dev-minimal.txt'
    reqs_dev = 'requirements-dev.txt'

    ret: list[Depends] = []
    if os.path.exists(reqs_minimal) and os.path.exists(reqs):
        ret.extend(python.from_reqs_file('DEPENDS', reqs_minimal))
        ret.extend(python.from_reqs_file('REQUIRES', reqs))
    elif os.path.exists(reqs):
        ret.extend(python.from_reqs_file('REQUIRES', reqs))

    if os.path.exists(reqs_dev_minimal) and os.path.exists(reqs_dev):
        ret.extend(python.from_reqs_file('DEPENDS_DEV', reqs_dev_minimal))
        ret.extend(python.from_reqs_file('REQUIRES_DEV', reqs_dev))
    elif os.path.exists(reqs_dev):
        ret.extend(python.from_reqs_file('DEPENDS_DEV', reqs_dev))

    return tuple(ret)
