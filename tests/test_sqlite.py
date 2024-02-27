import sqlite3
import unittest
from mock import patch
from datetime import date
from A2O4 import sqlite, common


def setup_db(path_to_fixture: str = None) -> tuple[sqlite3.Connection, sqlite3.Cursor]:
    con = sqlite3.connect(":memory:")
    cursor = con.cursor()
    with open("database_setup.sql", "r") as base_db_setup:
        base_db_setup = base_db_setup.read()
        cursor.executescript(base_db_setup)
    if path_to_fixture:
        with open(path_to_fixture, "r") as fixture:
            fixture = fixture.read()
        cursor.executescript(fixture)
    return (con, con.cursor())


class sqlite_test(unittest.TestCase):
    @patch("A2O4.sqlite.connect_to_db")
    def test_add_work_with_no_series(self, mock_db):
        (con, cur) = setup_db()
        mock_db.return_value = (con, cur)

        work = common.DB_Work(
            1234, "Work 1", ["Bob Bobbert", "January"], [], [], ["bg3", "poke"]
        )

        sqlite.add_work(work, con_cur=(con, cur))

        work_table = cur.execute("SELECT * FROM work").fetchall()
        fandom_table = cur.execute("SELECT * FROM fandom").fetchall()
        author_table = cur.execute("SELECT * FROM author").fetchall()
        work_fandom_link_table = cur.execute(
            "SELECT * FROM work_fandom_link"
        ).fetchall()
        work_author_link_table = cur.execute(
            "SELECT * FROM work_author_link"
        ).fetchall()
        cur.close()

        self.assertListEqual(work_table, [(1234, "Work 1", date.today().isoformat())])
        self.assertListEqual(fandom_table, [("bg3",), ("poke",)])
        self.assertListEqual(author_table, [("Bob Bobbert",), ("January",)])
        self.assertListEqual(
            work_fandom_link_table, [(1, 1234, "bg3"), (2, 1234, "poke")]
        )
        self.assertListEqual(
            work_author_link_table, [(1, 1234, "Bob Bobbert"), (2, 1234, "January")]
        )

    @patch("A2O4.sqlite.connect_to_db")
    def test_add_multiple_works_with_no_series(self, mock_db):
        (con, cur) = setup_db()
        mock_db.return_value = (con, cur)

        work_1 = common.DB_Work(
            1234, "Work 1", ["Bob Bobbert", "January"], [], [], ["bg3", "poke"]
        )
        work_2 = common.DB_Work(
            4321, "Work 2", ["February", "January"], [], [], ["bg3", "frank"]
        )

        sqlite.add_work(work_1, con_cur=(con, cur))
        sqlite.add_work(work_2, con_cur=(con, cur))

        work_table = cur.execute("SELECT * FROM work").fetchall()
        fandom_table = cur.execute("SELECT * FROM fandom").fetchall()
        author_table = cur.execute("SELECT * FROM author").fetchall()
        work_fandom_link_table = cur.execute(
            "SELECT * FROM work_fandom_link"
        ).fetchall()
        work_author_link_table = cur.execute(
            "SELECT * FROM work_author_link"
        ).fetchall()
        cur.close()

        self.assertListEqual(
            work_table,
            [
                (1234, "Work 1", date.today().isoformat()),
                (4321, "Work 2", date.today().isoformat()),
            ],
        )
        self.assertListEqual(fandom_table, [("bg3",), ("poke",), ("frank",)])
        self.assertListEqual(
            author_table, [("Bob Bobbert",), ("January",), ("February",)]
        )
        self.assertListEqual(
            work_fandom_link_table,
            [(1, 1234, "bg3"), (2, 1234, "poke"), (3, 4321, "bg3"), (4, 4321, "frank")],
        )
        self.assertListEqual(
            work_author_link_table,
            [
                (1, 1234, "Bob Bobbert"),
                (2, 1234, "January"),
                (3, 4321, "February"),
                (4, 4321, "January"),
            ],
        )

    @patch("A2O4.sqlite.connect_to_db")
    def test_add_work_with_series(self, mock_db):
        (con, cur) = setup_db()
        mock_db.return_value = (con, cur)

        work = common.DB_Work(
            1234,
            "Work 1",
            ["Bob Bobbert", "January"],
            [
                common.DB_Series(
                    12, "Series 1", ["Bob Bobbert", "January"], ["bg3", "poke"]
                )
            ],
            [1],
            ["bg3", "poke"],
        )

        sqlite.add_work(work, con_cur=(con, cur))

        work_table = cur.execute("SELECT * FROM work").fetchall()
        fandom_table = cur.execute("SELECT * FROM fandom").fetchall()
        author_table = cur.execute("SELECT * FROM author").fetchall()
        series_table = cur.execute("SELECT * FROM series").fetchall()
        work_fandom_link_table = cur.execute(
            "SELECT * FROM work_fandom_link"
        ).fetchall()
        work_author_link_table = cur.execute(
            "SELECT * FROM work_author_link"
        ).fetchall()
        series_work_link_table = cur.execute(
            "SELECT * FROM series_work_link"
        ).fetchall()
        series_fandom_link_table = cur.execute(
            "SELECT * FROM series_fandom_link"
        ).fetchall()
        series_author_link_table = cur.execute(
            "SELECT * FROM series_author_link"
        ).fetchall()
        cur.close()

        self.assertListEqual(work_table, [(1234, "Work 1", date.today().isoformat())])
        self.assertListEqual(series_table, [(12, "Series 1")])
        self.assertListEqual(fandom_table, [("bg3",), ("poke",)])
        self.assertListEqual(author_table, [("Bob Bobbert",), ("January",)])
        self.assertListEqual(
            work_fandom_link_table, [(1, 1234, "bg3"), (2, 1234, "poke")]
        )
        self.assertListEqual(
            work_author_link_table, [(1, 1234, "Bob Bobbert"), (2, 1234, "January")]
        )
        self.assertListEqual(series_work_link_table, [(1, 12, 1234, 1)])
        self.assertListEqual(
            series_fandom_link_table, [(1, 12, "bg3"), (2, 12, "poke")]
        )
        self.assertListEqual(
            series_author_link_table, [(1, 12, "Bob Bobbert"), (2, 12, "January")]
        )

    @patch("A2O4.sqlite.connect_to_db")
    def test_add_series(self, mock_db):
        (con, cur) = setup_db()
        mock_db.return_value = (con, cur)

        series = common.DB_Series(
            6543, "Series 1", ["Bobbert", "Jade"], ["bg3", "poke"]
        )
        work_1 = common.DB_Work(1234, "Work 1", ["Bobbert"], [series], [1], ["bg3"])
        work_2 = common.DB_Work(4321, "Work 2", ["Jade"], [series], [2], ["poke"])

        sqlite.add_series(series, [work_1, work_2], (con, cur))

        work_table = cur.execute("SELECT * FROM work").fetchall()
        fandom_table = cur.execute("SELECT * FROM fandom").fetchall()
        author_table = cur.execute("SELECT * FROM author").fetchall()
        series_table = cur.execute("SELECT * FROM series").fetchall()
        work_fandom_link_table = cur.execute(
            "SELECT * FROM work_fandom_link"
        ).fetchall()
        work_author_link_table = cur.execute(
            "SELECT * FROM work_author_link"
        ).fetchall()
        series_work_link_table = cur.execute(
            "SELECT * FROM series_work_link"
        ).fetchall()
        series_fandom_link_table = cur.execute(
            "SELECT * FROM series_fandom_link"
        ).fetchall()
        series_author_link_table = cur.execute(
            "SELECT * FROM series_author_link"
        ).fetchall()
        cur.close()

        self.assertListEqual(
            work_table,
            [
                (1234, "Work 1", date.today().isoformat()),
                (4321, "Work 2", date.today().isoformat()),
            ],
        )
        self.assertListEqual(series_table, [(6543, "Series 1")])
        self.assertListEqual(fandom_table, [("bg3",), ("poke",)])
        self.assertListEqual(author_table, [("Bobbert",), ("Jade",)])
        self.assertListEqual(
            work_fandom_link_table, [(1, 1234, "bg3"), (2, 4321, "poke")]
        )
        self.assertListEqual(
            work_author_link_table, [(1, 1234, "Bobbert"), (2, 4321, "Jade")]
        )
        self.assertListEqual(
            series_work_link_table, [(1, 6543, 1234, 1), (2, 6543, 4321, 2)]
        )
        self.assertListEqual(
            series_fandom_link_table, [(1, 6543, "bg3"), (2, 6543, "poke")]
        )
        self.assertListEqual(
            series_author_link_table, [(1, 6543, "Bobbert"), (2, 6543, "Jade")]
        )

    @patch("A2O4.sqlite.connect_to_db")
    def test_delete_work(self, mock_db):
        (con, cur) = setup_db("tests/fixtures/sqlite/delete_test.sql")
        mock_db.return_value = (con, cur)

        sqlite.delete_work(123456, (con, cur))

        work_table = cur.execute("SELECT * FROM work").fetchall()
        fandom_table = cur.execute("SELECT * FROM fandom").fetchall()
        author_table = cur.execute("SELECT * FROM author").fetchall()
        series_table = cur.execute("SELECT * FROM series").fetchall()
        work_fandom_link_table = cur.execute(
            "SELECT * FROM work_fandom_link"
        ).fetchall()
        work_author_link_table = cur.execute(
            "SELECT * FROM work_author_link"
        ).fetchall()
        series_work_link_table = cur.execute(
            "SELECT * FROM series_work_link"
        ).fetchall()
        series_fandom_link_table = cur.execute(
            "SELECT * FROM series_fandom_link"
        ).fetchall()
        series_author_link_table = cur.execute(
            "SELECT * FROM series_author_link"
        ).fetchall()
        cur.close()

        self.assertListEqual(
            work_table,
            [(234567, "Work 2", "2024-02-02"), (345678, "Work 3", "2024-02-02")],
        )
        self.assertListEqual(fandom_table, [("Fandom 1",), ("Fandom 2",)])
        self.assertListEqual(author_table, [("Author 1",), ("Author 2",)])
        self.assertListEqual(series_table, [(654321, "Series 1"), (765432, "Series 2")])
        self.assertListEqual(
            work_fandom_link_table, [(2, 234567, "Fandom 1"), (3, 345678, "Fandom 2")]
        )
        self.assertListEqual(
            work_author_link_table, [(2, 345678, "Author 1"), (3, 234567, "Author 2")]
        )
        self.assertListEqual(
            series_work_link_table, [(2, 654321, 234567, 2), (3, 765432, 345678, 1)]
        )
        self.assertListEqual(
            series_fandom_link_table,
            [
                (1, 654321, "Fandom 1"),
                (2, 654321, "Fandom 2"),
                (3, 765432, "Fandom 1"),
                (4, 765432, "Fandom 2"),
            ],
        )
        self.assertListEqual(
            series_author_link_table, [(1, 654321, "Author 1"), (2, 765432, "Author 2")]
        )

    @patch("A2O4.sqlite.connect_to_db")
    def test_delete_series(self, mock_db):
        (con, cur) = setup_db("tests/fixtures/sqlite/delete_test.sql")
        mock_db.return_value = (con, cur)

        sqlite.delete_series(654321, (con, cur))

        work_table = cur.execute("SELECT * FROM work").fetchall()
        fandom_table = cur.execute("SELECT * FROM fandom").fetchall()
        author_table = cur.execute("SELECT * FROM author").fetchall()
        series_table = cur.execute("SELECT * FROM series").fetchall()
        work_fandom_link_table = cur.execute(
            "SELECT * FROM work_fandom_link"
        ).fetchall()
        work_author_link_table = cur.execute(
            "SELECT * FROM work_author_link"
        ).fetchall()
        series_work_link_table = cur.execute(
            "SELECT * FROM series_work_link"
        ).fetchall()
        series_fandom_link_table = cur.execute(
            "SELECT * FROM series_fandom_link"
        ).fetchall()
        series_author_link_table = cur.execute(
            "SELECT * FROM series_author_link"
        ).fetchall()
        cur.close()

        self.assertListEqual(work_table, [(345678, "Work 3", "2024-02-02")])
        self.assertListEqual(fandom_table, [("Fandom 1",), ("Fandom 2",)])
        self.assertListEqual(author_table, [("Author 1",), ("Author 2",)])
        self.assertListEqual(series_table, [(765432, "Series 2")])
        self.assertListEqual(work_fandom_link_table, [(3, 345678, "Fandom 2")])
        self.assertListEqual(work_author_link_table, [(2, 345678, "Author 1")])
        self.assertListEqual(series_work_link_table, [(3, 765432, 345678, 1)])
        self.assertListEqual(
            series_fandom_link_table, [(3, 765432, "Fandom 1"), (4, 765432, "Fandom 2")]
        )
        self.assertListEqual(series_author_link_table, [(2, 765432, "Author 2")])


if __name__ == "__main__":
    unittest.main()
