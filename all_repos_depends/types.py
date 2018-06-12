from typing import NamedTuple
from typing import Tuple


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
    packages: Tuple[Package, ...]
    depends: Tuple[Depends, ...]
    errors: Tuple[str, ...]
