import sqlite3
from datetime import datetime
from os.path import exists
from . import common

def create_database() -> None:
    if exists('db.sqlite'):
        return
    
    print("Creating database file")
    with open('database_setup.sql', 'r') as sql_file:
        sql_script = sql_file.read()

    db = sqlite3.connect('db.sqlite')
    cursor = db.cursor()
    cursor.executescript(sql_script)
    db.commit()
    db.close()

def connect_to_db() -> tuple[sqlite3.Connection, sqlite3.Cursor]:
    con = sqlite3.connect('db.sqlite')
    return (con, con.cursor())

def add_work(work: common.DB_Work) -> None:
    (con, cur) = connect_to_db()
    currentDateTime = datetime.now().date()
    cur.execute(f"INSERT INTO work VALUES ({work.id}, \"{work.title}\", \"{currentDateTime}\")")

    for fandom in work.fandoms:
        cur.execute(f"INSERT OR IGNORE INTO fandom VALUES (\"{fandom}\")")
        cur.execute(f"INSERT OR IGNORE INTO work_fandom_link (work_id, fandom_name) VALUES ({work.id}, \"{fandom}\")")
    for author in work.authors:
        cur.execute(f"INSERT OR IGNORE INTO author VALUES (\"{author}\")")
        cur.execute(f"INSERT OR IGNORE INTO work_author_link (work_id, author_name) VALUES ({work.id}, \"{author}\")")
    for (series, part) in zip(work.series_list, work.parts):
        cur.execute(f"INSERT OR IGNORE INTO series VALUES ({series.id}, \"{series.title}\")")
        cur.execute(f"INSERT OR IGNORE INTO series_work_link (series_id, work_id, part) VALUES ({series.id}, {work.id}, {part})")
        for fandom in work.fandoms:
            cur.execute(f"INSERT OR IGNORE INTO series_fandom_link (series_id, fandom_name) VALUES ({series.id}, \"{fandom}\")")
        for author in series.authors:
            cur.execute(f"INSERT OR IGNORE INTO series_author_link (series_id, author_name) VALUES ({series.id}, \"{author}\")")
    
    con.commit()
    con.close()

def add_series(series: common.DB_Series, works: list[common.DB_Work]) -> None:
    (con, cur) = connect_to_db()
    currentDateTime = datetime.now().date()

    cur.execute(f"INSERT OR IGNORE INTO series VALUES ({series.id}, \"{series.title}\")")
    series_sql = "INSERT OR IGNORE INTO series_work_link (series_id, work_id, part) VALUES"
    part = 1
    for work in works:
        if part == 1:
            series_sql = f"{series_sql} ({series.id}, {work.id}, {part})"
        else:
            series_sql = f"{series_sql}, ({series.id}, {work.id}, {part})"
        part = part + 1
    cur.execute(series_sql)

    for fandom in series.fandoms: 
        cur.execute(f"INSERT OR IGNORE INTO fandom VALUES (\"{fandom}\")")
        cur.execute(f"INSERT OR IGNORE INTO series_fandom_link (series_id, fandom_name) VALUES ({series.id}, \"{fandom}\")")

    for author in series.authors:
        cur.execute(f"INSERT OR IGNORE INTO author VALUES (\"{author}\")")
        cur.execute(f"INSERT OR IGNORE INTO series_author_link (series_id, author_name) VALUES ({work.id}, \"{author}\")")

    for work in works:
        cur.execute(f"INSERT INTO work VALUES ({work.id}, \"{work.title}\", \"{currentDateTime}\")")

        for fandom in work.fandoms:
            cur.execute(f"INSERT OR IGNORE INTO work_fandom_link (work_id, fandom_name) VALUES ({work.id}, \"{fandom}\")")
        for author in work.authors:
            cur.execute(f"INSERT OR IGNORE INTO author VALUES (\"{author}\")")
            cur.execute(f"INSERT OR IGNORE INTO work_author_link (work_id, author_name) VALUES ({work.id}, \"{author}\")")
        for (work_series, part) in zip(work.series_list, work.parts):
            if (work_series.title == series.title): continue
            cur.execute(f"INSERT OR IGNORE INTO series VALUES ({work_series.id}, \"{work_series.title}\")")
            cur.execute(f"INSERT OR IGNORE INTO series_work_link (series_id, work_id, part) VALUES ({work_series.id}, {work.id}, {part})")
            for fandom in work.fandoms:
                cur.execute(f"INSERT OR IGNORE INTO series_fandom_link (series_id, fandom_name) VALUES ({series.id}, \"{fandom}\")")
            for author in series.authors:
                cur.execute(f"INSERT OR IGNORE INTO series_author_link (series_id, author_name) VALUES ({series.id}, \"{author}\")")
    
    con.commit()
    con.close()
    

def add_work_to_device(work_id: str, device: str) -> None:
    (con, cur) = connect_to_db()
    currentDateTime = datetime.now().date()
    
    cur.execute(f"INSERT OR IGNORE INTO device VALUES (\"{device}\")")
    cur.execute(f"INSERT INTO device_work_link (device_name, work_id, work_last_updated) VALUES (\"{device}\", {work_id}, \"{currentDateTime}\")")

    con.commit()
    con.close()

#TODO
def add_series_to_device(series_id: str, device: str) -> None:
    (con, cur) = connect_to_db()
    currentDateTime = datetime.now().date()

    cur.execute(f"INSERT OR IGNORE INTO device VALUES (\"{device}\")")

def get_work(id: int, con_cur: tuple[sqlite3.Connection, sqlite3.Cursor] = None) -> common.DB_Work:
    con: sqlite3.Connection
    cur: sqlite3.Cursor
    
    if (con_cur):
        (con, cur) = con_cur
    else:
        (con, cur) = connect_to_db()
    
    work_name = cur.execute("SELECT name FROM work WHERE id = ?;", (id,)).fetchone()[0]

    fandoms = list(set(map(
        lambda fandom: fandom[0],
        cur.execute("SELECT fandom_name FROM work_fandom_link WHERE work_id = ?", (id,)).fetchall()
    )))
    authors = list(set(map(
        lambda author: author[0],
        cur.execute("SELECT author_name FROM work_author_link WHERE work_id = ?", (id,)).fetchall()
    )))
    all_series = cur.execute(
        """SELECT Series.id, Link.part
        FROM series_work_link AS Link
        JOIN series AS Series on Link.series_id=Series.id
        WHERE Link.work_id = ?""", 
        (id,)
    ).fetchall()
    parts: list[int] = []
    full_series: list[common.DB_Series] = []

    for series in all_series:
        full_series.append(get_series(series[0]))
        parts.append(series[1])

    if (not con_cur):
        con.close()
    return common.DB_Work(id, work_name, authors, parts, full_series, fandoms)

def get_series(id: int) -> common.DB_Series:
    (con, cur) = connect_to_db()

    name = cur.execute("SELECT name FROM series WHERE id = ?", (id,)).fetchone()[0]
    authors = list(set(map(
        lambda author: author[0],
        cur.execute("SELECT author_name FROM series_author_link WHERE series_id = ?", (id,)).fetchall()
    )))
    fandoms = list(set(map(
        lambda fandom: fandom[0],
        cur.execute("SELECT fandom_name FROM series_fandom_link WHERE series_id = ?", (id,)).fetchall()
    )))
    
    return common.DB_Series(id, name, authors, fandoms)

def delete_work(id: int, con_cur: tuple[sqlite3.Connection, sqlite3.Cursor] = None) -> None:
    con: sqlite3.Connection
    cur: sqlite3.Cursor

    if (con_cur):
        (con, cur) = con_cur
    else:
        (con, cur) = connect_to_db()

    #work = get_work(id, (con, cur))

    cur.execute('DELETE FROM work WHERE id = ?', (id,))
    cur.execute("DELETE FROM work_author_link WHERE work_id = ?", (id,))
    cur.execute("DELETE FROM work_fandom_link WHERE work_id = ?", (id,))
    cur.execute("DELETE FROM series_work_link WHERE work_id = ?", (id,))
    cur.execute("DELETE FROM device_work_link WHERE work_id = ?", (id,))

    # for author in work.authors:
    #     #print(author)
    #     num_work_links = cur.execute("SELECT COUNT(*) FROM work_author_link WHERE author_name = ?", (author,)).fetchone()[0]
    #     #print(num_work_links)
    #     if (num_work_links != 0):
    #         continue
    #     num_series_links = cur.execute("SELECT COUNT(*) FROM series_author_link WHERE author_name = ?", (author,)).fetchone()[0] 
    #     #print(num_series_links)
    #     if (num_series_links != 0):
    #         continue
    #     cur.execute("DELETE FROM author WHERE name = ?", (author,))
    
    # #print()

    # for fandom in work.fandoms:
    #     #print(fandom)
    #     num_work_links = cur.execute("SELECT COUNT(*) FROM work_fandom_link WHERE fandom_name = ?", (fandom,)).fetchone()[0]
    #     #print(num_work_links)
    #     if (num_work_links != 0):
    #         continue
    #     num_series_links = cur.execute("SELECT COUNT(*) FROM series_fandom_link WHERE fandom_name = ?", (fandom,)).fetchone()[0] 
    #     #print(num_series_links)
    #     if (num_series_links != 0):
    #         continue
    #     cur.execute("DELETE FROM fandom WHERE name = ?", (fandom,))

    #con.commit()
    if (not con_cur):
        con.close()

def delete_series(id: int, con_cur: tuple[sqlite3.Connection, sqlite3.Cursor] = None) -> None:
    con: sqlite3.Connection
    cur: sqlite3.Cursor

    if (con_cur):
        (con, cur) = con_cur
    else:
        (con, cur) = connect_to_db()

    cur.execute("DELETE FROM series WHERE id = ?", (id,))

    works_in_series = cur.execute("SELECT work_id FROM series_work_link WHERE series_id = ?", (id,)).fetchall()

    for work in works_in_series:
        delete_work(work[0], (con, cur))
    
    cur.execute("DELETE FROM series_work_link WHERE series_id = ?", (id,))
    cur.execute("DELETE FROM series_author_link where series_id = ?", (id,))
    cur.execute("DELETE FROM series_fandom_link where series_id = ?", (id,))

    #con.commit()
    if (not con_cur):
        con.close()