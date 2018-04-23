import collections
import json

from all_repos.config import load_config as all_repos_load_config


def _fn(s):
    mod, _, name = s.rpartition('.')
    return getattr(__import__(mod, fromlist=['_trash']), name)


Config = collections.namedtuple(
    'Config',
    (
        'all_repos_config',
        'get_packages',
        'get_depends',
    ),
)


def load_config(filename):
    with open(filename) as f:
        cfg = json.load(f)

    return Config(
        all_repos_config=all_repos_load_config(cfg['all_repos_config']),
        get_packages=tuple(_fn(f) for f in cfg['get_packages']),
        get_depends=tuple(_fn(f) for f in cfg['get_depends']),
    )
