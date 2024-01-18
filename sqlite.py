import sqlite3
import common
from datetime import datetime
from os.path import exists

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
        
    
