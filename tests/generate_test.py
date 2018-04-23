import sqlite3


def test_output(generated):
    with sqlite3.connect(generated) as db:
        # should have generated some data
        assert db.execute('SELECT * FROM repos').fetchall()
        assert db.execute('SELECT * FROM packages').fetchall()
        assert db.execute('SELECT * FROM depends').fetchall()
        assert db.execute('SELECT * FROM errors').fetchall()

        # r1 depends on pkg2
        query = (
            'SELECT COUNT(1) FROM depends\n'
            'WHERE repo_name = "r1" AND package_key = "pkg2"\n'
        )
        count, = db.execute(query).fetchone()
        assert count == 1

        # should not have anything about r4 since it was empty
        query = 'SELECT COUNT(1) FROM packages WHERE repo_name = "r4"'
        count, = db.execute(query).fetchone()
        assert count == 0
        query = 'SELECT COUNT(1) FROM depends WHERE repo_name = "r4"'
        count, = db.execute(query).fetchone()
        assert count == 0

        # should only have one error
        count, = db.execute('SELECT COUNT(1) FROM errors').fetchone()
        assert count == 1
