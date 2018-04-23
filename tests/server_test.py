import sqlite3

import pyquery
import pytest

from all_repos_depends import server
from all_repos_depends.types import Depends
from all_repos_depends.types import Package


@pytest.fixture(scope='module', autouse=True)
def app_db_context(generated):
    server.app.database_path = generated
    yield
    del server.app.database_path


@pytest.fixture
def db(generated):
    with sqlite3.connect(generated) as db:
        yield db


def test_list_repos(db):
    assert server.list_repos(db) == ['r1', 'r2', 'r3', 'r5']


def test_list_packages(db):
    assert server.list_packages(db) == ['pkg1', 'pkg2']


def test_list_external(db):
    assert server.list_external(db) == ['pre-commit', 'pytest', 'six']


def test_index():
    resp = pyquery.PyQuery(server.index())
    assert resp.find('#repos')
    assert resp.find('#packages')
    assert resp.find('#external')


def test_repo_packages(db):
    ret = server.repo_packages(db, 'r1')
    assert ret == [Package('python', 'pkg1', 'pkg1')]
    assert server.repo_packages(db, 'r3') == []


def test_repo_depends(db):
    assert server.repo_depends(db, 'r1') == [
        Depends('DEPENDS', 'python', 'pkg2', ''),
        Depends('DEPENDS', 'python', 'six', ''),
    ]
    assert server.repo_depends(db, 'r2') == [
        Depends('DEPENDS_DEV', 'python', 'pre-commit', ''),
        Depends('DEPENDS_DEV', 'python', 'pytest', ''),
    ]


def test_repo_rdepends(db):
    assert server.repo_rdepends(db, 'r2') == [
        ('r1', Depends('DEPENDS', 'python', 'pkg2', '')),
    ]
    assert server.repo_rdepends(db, 'r1') == []


def test_repo():
    resp = pyquery.PyQuery(server.repo('r1'))
    assert resp.find('h3:contains("provided packages")')
    assert resp.find('h3:contains("dependencies")')


def test_package_repo_names(db):
    assert server.package_repo_names(db, 'pkg1') == ['r1']
    assert server.package_repo_names(db, 'pkg2') == ['r2', 'r5']
    assert server.package_repo_names(db, 'six') == []


def test_package_rdepends(db):
    expected = [('r1', Depends('DEPENDS', 'python', 'six', ''))]
    assert server.package_rdepends(db, 'six') == expected


def test_pkg_redirect():
    resp = pyquery.PyQuery(server.pkg('pkg1'))
    meta = resp.find('meta[http-equiv="refresh"]')
    assert meta.attr('content') == '0;/repo/r1'


def test_pkg_disambituate():
    resp = pyquery.PyQuery(server.pkg('pkg2'))
    repo_links = resp.find('a[href^="/repo/"]')
    assert len(repo_links) == 2
    assert repo_links.eq(0).attr('href') == '/repo/r2'
    assert repo_links.eq(1).attr('href') == '/repo/r5'


def test_pkg_external():
    resp = pyquery.PyQuery(server.pkg('six'))
    assert resp.find('h2:contains("external package: six")')
