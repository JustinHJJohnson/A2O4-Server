import sqlite3
import unittest
from mock import patch
from A2O4 import ao3, sqlite

def setup_db(path_to_fixture: str) -> tuple[sqlite3.Connection, sqlite3.Cursor]:
    con = sqlite3.connect(":memory:")
    cursor = con.cursor()
    with open('database_setup.sql', 'r') as base_db_setup:
        base_db_setup = base_db_setup.read()
    with open(path_to_fixture, 'r') as fixture:
        fixture = fixture.read()
    cursor.executescript(base_db_setup)
    cursor.executescript(fixture)
    return (con, con.cursor())

class sqlite_test(unittest.TestCase):
    @patch('A2O4.sqlite.connect_to_db')
    def test_delete_work(self, mock_db):
        (con, cur) = setup_db('tests/fixtures/sqlite/delete_test.sql')
        
        mock_db.return_value = (con, cur)

        sqlite.delete_work(123456, (con, cur))

        work_table = cur.execute("SELECT * FROM work").fetchall()
        fandom_table = cur.execute("SELECT * FROM fandom").fetchall()
        author_table = cur.execute("SELECT * FROM author").fetchall()
        series_table = cur.execute("SELECT * FROM series").fetchall()
        work_fandom_link_table = cur.execute("SELECT * FROM work_fandom_link").fetchall()
        work_author_link_table = cur.execute("SELECT * FROM work_author_link").fetchall()
        series_work_link_table = cur.execute("SELECT * FROM series_work_link").fetchall()
        series_fandom_link_table = cur.execute("SELECT * FROM series_fandom_link").fetchall()
        series_author_link_table = cur.execute("SELECT * FROM series_author_link").fetchall()
        cur.close()
        
        self.assertListEqual(work_table, [(234567, "Work 2", "2024-02-02"), (345678, "Work 3", "2024-02-02")])
        self.assertListEqual(fandom_table, [("Fandom 1",), ("Fandom 2",)])
        self.assertListEqual(author_table, [("Author 1",), ("Author 2",)])
        self.assertListEqual(series_table, [(654321, "Series 1"), (765432, "Series 2")])
        self.assertListEqual(work_fandom_link_table, [(2, 234567, "Fandom 1"), (3, 345678, "Fandom 2")])
        self.assertListEqual(work_author_link_table, [(2, 345678, "Author 1"), (3, 234567, "Author 2")])
        self.assertListEqual(series_work_link_table, [(2, 654321, 234567, 2), (3, 765432, 345678, 1)])
        self.assertListEqual(series_fandom_link_table, [(1, 654321, "Fandom 1"), (2, 654321, "Fandom 2"), (3, 765432, "Fandom 1"), (4, 765432, "Fandom 2")])
        self.assertListEqual(series_author_link_table, [(1, 654321, "Author 1"), (2, 765432, "Author 2")])

    @patch('A2O4.sqlite.connect_to_db')
    def test_delete_series(self, mock_db):
        (con, cur) = setup_db('tests/fixtures/sqlite/delete_test.sql')
        
        mock_db.return_value = (con, cur)

        sqlite.delete_series(654321, (con, cur))

        work_table = cur.execute("SELECT * FROM work").fetchall()
        fandom_table = cur.execute("SELECT * FROM fandom").fetchall()
        author_table = cur.execute("SELECT * FROM author").fetchall()
        series_table = cur.execute("SELECT * FROM series").fetchall()
        work_fandom_link_table = cur.execute("SELECT * FROM work_fandom_link").fetchall()
        work_author_link_table = cur.execute("SELECT * FROM work_author_link").fetchall()
        series_work_link_table = cur.execute("SELECT * FROM series_work_link").fetchall()
        series_fandom_link_table = cur.execute("SELECT * FROM series_fandom_link").fetchall()
        series_author_link_table = cur.execute("SELECT * FROM series_author_link").fetchall()
        cur.close()
        
        self.assertListEqual(work_table, [(345678, "Work 3", "2024-02-02")])
        self.assertListEqual(fandom_table, [("Fandom 1",), ("Fandom 2",)])
        self.assertListEqual(author_table, [("Author 1",), ("Author 2",)])
        self.assertListEqual(series_table, [(765432, "Series 2")])
        self.assertListEqual(work_fandom_link_table, [(3, 345678, "Fandom 2")])
        self.assertListEqual(work_author_link_table, [(2, 345678, "Author 1")])
        self.assertListEqual(series_work_link_table, [(3, 765432, 345678, 1)])
        self.assertListEqual(series_fandom_link_table, [(3, 765432, "Fandom 1"), (4, 765432, "Fandom 2")])
        self.assertListEqual(series_author_link_table, [(2, 765432, "Author 2")])


if __name__ == '__main__':
    unittest.main()