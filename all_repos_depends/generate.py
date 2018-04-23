import argparse
import os.path
import sqlite3
import traceback

from all_repos.autofix_lib import cwd

from all_repos_depends.config import load_config
from all_repos_depends.errors import DependsError
from all_repos_depends.types import Repo


def get_repo_info(cfg, repo_name, repo_path):
    with cwd(repo_path):
        errors = []

        def _each(fns, augment):
            for fn in fns:
                try:
                    ret = fn()
                except DependsError:
                    errors.append(traceback.format_exc())
                else:
                    if ret:
                        augment(ret)

        packages = []
        _each(cfg.get_packages, packages.append)
        depends = []
        _each(cfg.get_depends, depends.extend)
        return Repo(repo_name, tuple(packages), tuple(depends), tuple(errors))


def create_schema(db):
    db.executescript(
        'CREATE TABLE repos (\n'
        '    name TEXT NOT NULL,\n'
        '    PRIMARY KEY (name)\n'
        ')',
    )
    db.executescript(
        'CREATE TABLE packages (\n'
        '    repo_name TEXT NOT NULL,\n'
        '    type TEXT NOT NULL,\n'
        '    key TEXT NOT NULL,\n'
        '    name TEXT NOT NULL,\n'
        '    PRIMARY KEY (repo_name, type, key)\n'
        ')',
    )
    db.executescript(
        'CREATE TABLE depends (\n'
        '    repo_name TEXT NOT NULL,\n'
        '    relationship TEXT NOT NULL,\n'
        '    package_type TEXT NOT NULL,\n'
        '    package_key TEXT NOT NULL,\n'
        '    spec TEXT NOT NULL\n'
        ')',
    )
    db.executescript(
        'CREATE TABLE errors (\n'
        '    repo_name TEXT NOT NULL,\n'
        '    trace BLOB\n'
        ')',
    )


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-C', '--config-filename',
        default='all-repos-depends.json',
    )
    parser.add_argument('--database', default='database.db')
    args = parser.parse_args(argv)

    cfg = load_config(args.config_filename)

    infos = []
    for repo in cfg.all_repos_config.get_cloned_repos():
        path = os.path.join(cfg.all_repos_config.output_dir, repo)
        infos.append(get_repo_info(cfg, repo, path))

    infos = [i for i in infos if i.packages or i.depends or i.errors]

    repos_rows = [(info.name,) for info in infos]
    packages_rows = []
    depends_rows = []
    errors_rows = []
    for info in infos:
        for package in info.packages:
            packages_rows.append((info.name,) + package)
        for depends in info.depends:
            depends_rows.append((info.name,) + depends)
        for error in info.errors:
            errors_rows.append((info.name, error))

    with sqlite3.connect(args.database) as db:
        create_schema(db)
        query = 'INSERT INTO repos VALUES (?)'
        db.executemany(query, repos_rows)
        query = 'INSERT INTO packages VALUES (?, ?, ?, ?)'
        db.executemany(query, packages_rows)
        query = 'INSERT INTO depends VALUES (?, ?, ?, ?, ?)'
        db.executemany(query, depends_rows)
        query = 'INSERT INTO errors VALUES (?, ?)'
        db.executemany(query, errors_rows)


if __name__ == '__main__':
    exit(main())
