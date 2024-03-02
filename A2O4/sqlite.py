import sqlite3
from datetime import date
from os.path import exists

from . import common


def create_database() -> None:
    if exists("db.sqlite"):
        return

    print("Creating database file")
    with open("database_setup.sql", "r") as sql_file:
        sql_script = sql_file.read()

    db = sqlite3.connect("db.sqlite")
    cursor = db.cursor()
    cursor.executescript(sql_script)
    db.commit()
    db.close()


class Database:
    con: sqlite3.Connection
    cur: sqlite3.Cursor

    def __init__(self) -> None:
        (self.con, self.cur) = self.__connect_to_db()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        self.commit()
        self.close()

    def __connect_to_db(self) -> tuple[sqlite3.Connection, sqlite3.Cursor]:
        con = sqlite3.connect("db.sqlite")
        return (con, con.cursor())

    def commit(self) -> None:
        self.con.commit()

    def close(self) -> None:
        self.con.close()

    def add_work(self, work: common.DB_Work, series_info: bool = True) -> None:
        currentDateTime = date.today().isoformat()

        fandom_rows: list[tuple[str]] = []
        author_rows: list[tuple[str]] = []
        series_row: list[tuple[int, str]] = []
        work_fandom_rows: list[tuple[int, str]] = []
        work_author_rows: list[tuple[int, str]] = []
        series_fandom_rows: list[tuple[int, str]] = []
        series_author_rows: list[tuple[int, str]] = []
        series_work_rows: list[tuple[int, int, int]] = []

        for fandom in work.fandoms:
            fandom_rows.append((fandom,))
            work_fandom_rows.append((work.id, fandom))
        for author in work.authors:
            author_rows.append((author,))
            work_author_rows.append((work.id, author))
        for series, part in zip(work.series_list, work.parts):
            series_row.append((series.id, series.title))
            series_work_rows.append((series.id, work.id, part))
            for fandom in work.fandoms:
                series_fandom_rows.append((series.id, fandom))
            for author in series.authors:
                series_author_rows.append((series.id, author))

        self.cur.execute(
            "INSERT INTO work VALUES (?, ?, ?)", (work.id, work.title, currentDateTime)
        )
        self.cur.executemany("INSERT OR IGNORE INTO series VALUES (?, ?)", series_row)
        self.cur.executemany("INSERT OR IGNORE INTO fandom VALUES (?)", fandom_rows)
        self.cur.executemany("INSERT OR IGNORE INTO author VALUES (?)", author_rows)

        self.cur.executemany(
            "INSERT OR IGNORE INTO work_fandom_link (work_id, fandom_name) VALUES (?, ?)",
            work_fandom_rows,
        )
        self.cur.executemany(
            "INSERT OR IGNORE INTO work_author_link (work_id, author_name) VALUES (?, ?)",
            work_author_rows,
        )

        if series_info:
            self.cur.executemany(
                "INSERT OR IGNORE INTO series_work_link (series_id, work_id, part) VALUES (?, ?, ?)",
                series_work_rows,
            )
            self.cur.executemany(
                "INSERT OR IGNORE INTO series_fandom_link (series_id, fandom_name) VALUES (?, ?)",
                series_fandom_rows,
            )
            self.cur.executemany(
                "INSERT OR IGNORE INTO series_author_link (series_id, author_name) VALUES (?, ?)",
                series_author_rows,
            )

    def add_series(
        self,
        series: common.DB_Series,
        works: list[common.DB_Work],
    ) -> None:
        fandom_rows: list[tuple[str]] = []
        author_rows: list[tuple[str]] = []
        series_fandom_rows: list[tuple[int, str]] = []
        series_author_rows: list[tuple[int, str]] = []
        series_work_rows: list[tuple[int, int, int]] = []

        for fandom in series.fandoms:
            fandom_rows.append((fandom,))
            series_fandom_rows.append((series.id, fandom))
        for author in series.authors:
            author_rows.append((author,))
            series_author_rows.append((series.id, author))

        for work in works:
            self.add_work(work, False)
            series_index = -1
            for i, s in enumerate(work.series_list):
                if s.title == series.title:
                    series_index = i
            series_work_rows.append((series.id, work.id, work.parts[series_index]))

        self.cur.executemany(
            "INSERT OR IGNORE INTO series_work_link (series_id, work_id, part) VALUES (?, ?, ?)",
            series_work_rows,
        )
        self.cur.executemany(
            "INSERT OR IGNORE INTO series_fandom_link (series_id, fandom_name) VALUES (?, ?)",
            series_fandom_rows,
        )
        self.cur.executemany(
            "INSERT OR IGNORE INTO series_author_link (series_id, author_name) VALUES (?, ?)",
            series_author_rows,
        )

    def add_work_to_device(self, work_id: int, device: str) -> None:
        currentDateTime = date.today().isoformat()

        self.cur.execute("INSERT OR IGNORE INTO device VALUES (?)", (device,))
        self.cur.execute(
            "INSERT INTO device_work_link (device_name, work_id, work_last_updated) VALUES (?, ?, ?)",
            (device, work_id, currentDateTime),
        )

    # TODO
    def add_series_to_device(self, series_id: int, device: str) -> None:
        # currentDateTime = date.today().isoformat()

        self.cur.execute("INSERT OR IGNORE INTO device VALUES (?)", (device,))

    def get_work(self, id: int) -> common.DB_Work:
        work_name = self.cur.execute(
            "SELECT name FROM work WHERE id = ?", (id,)
        ).fetchone()[0]

        fandoms = list(
            set(
                map(
                    lambda fandom: fandom[0],
                    self.cur.execute(
                        "SELECT fandom_name FROM work_fandom_link WHERE work_id = ?",
                        (id,),
                    ).fetchall(),
                )
            )
        )
        authors = list(
            set(
                map(
                    lambda author: author[0],
                    self.cur.execute(
                        "SELECT author_name FROM work_author_link WHERE work_id = ?",
                        (id,),
                    ).fetchall(),
                )
            )
        )
        all_series = self.cur.execute(
            """SELECT Series.id, Link.part
            FROM series_work_link AS Link
            JOIN series AS Series on Link.series_id=Series.id
            WHERE Link.work_id = ?""",
            (id,),
        ).fetchall()
        parts: list[int] = []
        full_series: list[common.DB_Series] = []

        for series in all_series:
            full_series.append(self.get_series(series[0]))
            parts.append(series[1])

        return common.DB_Work(id, work_name, authors, full_series, parts, fandoms)

    def get_series(self, id: int) -> common.DB_Series:
        name = self.cur.execute(
            "SELECT name FROM series WHERE id = ?", (id,)
        ).fetchone()[0]
        authors = list(
            set(
                map(
                    lambda author: author[0],
                    self.cur.execute(
                        "SELECT author_name FROM series_author_link WHERE series_id = ?",
                        (id,),
                    ).fetchall(),
                )
            )
        )
        fandoms = list(
            set(
                map(
                    lambda fandom: fandom[0],
                    self.cur.execute(
                        "SELECT fandom_name FROM series_fandom_link WHERE series_id = ?",
                        (id,),
                    ).fetchall(),
                )
            )
        )

        return common.DB_Series(id, name, authors, fandoms)

    def delete_work(self, id: int) -> None:
        self.cur.execute("DELETE FROM work WHERE id = ?", (id,))
        self.cur.execute("DELETE FROM work_author_link WHERE work_id = ?", (id,))
        self.cur.execute("DELETE FROM work_fandom_link WHERE work_id = ?", (id,))
        self.cur.execute("DELETE FROM series_work_link WHERE work_id = ?", (id,))
        self.cur.execute("DELETE FROM device_work_link WHERE work_id = ?", (id,))

    def delete_series(self, id: int) -> None:
        self.cur.execute("DELETE FROM series WHERE id = ?", (id,))

        works_in_series = self.cur.execute(
            "SELECT work_id FROM series_work_link WHERE series_id = ?", (id,)
        ).fetchall()

        for work in works_in_series:
            self.delete_work(work[0])

        self.cur.execute("DELETE FROM series_work_link WHERE series_id = ?", (id,))
        self.cur.execute("DELETE FROM series_author_link where series_id = ?", (id,))
        self.cur.execute("DELETE FROM series_fandom_link where series_id = ?", (id,))
