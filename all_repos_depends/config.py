from __future__ import annotations

import json
from typing import Any
from typing import Callable
from typing import NamedTuple

from all_repos.config import Config as AllReposConfig
from all_repos.config import load_config as all_repos_load_config

from all_repos_depends.types import Depends
from all_repos_depends.types import Package


def _fn(s: str) -> Callable[..., Any]:
    mod, _, name = s.rpartition('.')
    return getattr(__import__(mod, fromlist=['_trash']), name)


class Config(NamedTuple):
    all_repos_config: AllReposConfig
    get_packages: tuple[Callable[[], Package], ...]
    get_depends: tuple[Callable[[], tuple[Depends, ...]], ...]


def load_config(filename: str) -> Config:
    with open(filename) as f:
        cfg = json.load(f)

    return Config(
        all_repos_config=all_repos_load_config(cfg['all_repos_config']),
        get_packages=tuple(_fn(f) for f in cfg['get_packages']),
        get_depends=tuple(_fn(f) for f in cfg['get_depends']),
    )
