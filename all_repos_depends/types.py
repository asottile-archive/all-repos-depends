from __future__ import annotations

from typing import NamedTuple


class Package(NamedTuple):
    type: str
    key: str
    name: str


class Depends(NamedTuple):
    relationship: str
    package_type: str
    package_key: str
    spec: str


class Repo(NamedTuple):
    name: str
    packages: tuple[Package, ...]
    depends: tuple[Depends, ...]
    errors: tuple[str, ...]
