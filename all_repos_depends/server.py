import argparse
import sqlite3

import flask
import mako.lookup
import pkg_resources

from all_repos_depends.types import Depends
from all_repos_depends.types import Package


app = flask.Flask(__name__)

templates = pkg_resources.resource_filename('all_repos_depends', 'templates')
template_lookup = mako.lookup.TemplateLookup(
    directories=[templates],
    default_filters=['html_escape'],
    imports=['from mako.filters import html_escape'],
)


def render_template(template_name, **env):
    template = template_lookup.get_template(template_name)
    return template.render(**env)


def list_repos(db):
    query = 'SELECT name FROM repos ORDER BY name'
    return [name for name, in db.execute(query).fetchall()]


def list_packages(db):
    query = 'SELECT DISTINCT key FROM packages ORDER BY key'
    return [key for key, in db.execute(query).fetchall()]


def list_external(db):
    query = (
        'SELECT DISTINCT package_key FROM depends\n'
        'LEFT OUTER JOIN packages ON packages.key = depends.package_key\n'
        'WHERE packages.key IS NULL\n'
        'ORDER BY package_key\n'
    )
    return [key for key, in db.execute(query).fetchall()]


@app.route('/')
def index():
    with sqlite3.connect(app.database_path) as db:
        repos = list_repos(db)
        packages = list_packages(db)
        external = list_external(db)
    return render_template(
        'index.mako', repos=repos, packages=packages, external=external,
    )


def repo_packages(db, repo_name):
    query = 'SELECT * FROM packages WHERE repo_name = ? ORDER BY key'
    rows = db.execute(query, (repo_name,)).fetchall()
    return [Package(*row) for _, *row in rows]


def repo_depends(db, repo_name):
    query = (
        'SELECT * FROM depends WHERE repo_name = ?\n'
        'ORDER BY relationship, package_key'
    )
    rows = db.execute(query, (repo_name,)).fetchall()
    return [Depends(*row) for _, *row in rows]


def repo_rdepends(db, repo_name):
    query = (
        'SELECT depends.*\n'
        'FROM packages\n'
        'INNER JOIN depends ON depends.package_key = packages.key\n'
        'WHERE packages.repo_name = ?\n'
        'ORDER BY depends.repo_name\n'
    )
    rows = db.execute(query, (repo_name,)).fetchall()
    return [(repo_name, Depends(*row)) for repo_name, *row in rows]


@app.route('/repo/<path:repo_name>')
def repo(repo_name):
    repo_name = repo_name.rstrip('/')

    with sqlite3.connect(app.database_path) as db:
        packages = repo_packages(db, repo_name)
        depends = repo_depends(db, repo_name)
        rdepends = repo_rdepends(db, repo_name)

    return render_template(
        'repo.mako',
        repo_name=repo_name,
        packages=packages, depends=depends, rdepends=rdepends,
    )


def package_repo_names(db, pkgname):
    query = (
        'SELECT DISTINCT repo_name\n'
        'FROM packages\n'
        'WHERE key = ?\n'
        'ORDER BY repo_name, type\n'
    )
    rows = db.execute(query, (pkgname,)).fetchall()

    return [repo_name for repo_name, in rows]


def package_rdepends(db, pkgname):
    query = 'SELECT * FROM depends WHERE package_key = ? ORDER BY repo_name'
    rows = db.execute(query, (pkgname,))
    return [(repo_name, Depends(*row)) for repo_name, *row in rows]


@app.route('/pkg/<pkgname>')
def pkg(pkgname):
    with sqlite3.connect(app.database_path) as db:
        repo_names = package_repo_names(db, pkgname)
        if len(repo_names) == 1:
            return render_template('redirect.mako', repo_name=repo_names[0])
        elif len(repo_names) > 1:
            return render_template(
                'disambiguate.mako', pkgname=pkgname, repo_names=repo_names,
            )
        else:
            rdepends = package_rdepends(db, pkgname)
            return render_template(
                'external.mako', pkgname=pkgname, rdepends=rdepends,
            )


def main(argv=None):  # pragma: no cover (never returns)
    parser = argparse.ArgumentParser()
    parser.add_argument('--database', default='database.db')
    parser.add_argument('-p', '--port', type=int, default=5000)
    mutex = parser.add_mutually_exclusive_group()
    mutex.add_argument('--debug', action='store_true')
    mutex.add_argument('--processes', type=int, default=4)
    args = parser.parse_args(argv)

    app.database_path = args.database
    kwargs = {'port': args.port, 'debug': args.debug}
    if not args.debug:
        kwargs['processes'] = args.processes

    app.run('0.0.0.0', **kwargs)


if __name__ == '__main__':
    exit(main())
