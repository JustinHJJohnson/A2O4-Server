CREATE TABLE IF NOT EXISTS work(
  id INTEGER NOT NULL,
  name TEXT NOT NULL,
  last_updated TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS author(
  name TEXT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS series(
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS fandom(
 	name TEXT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS device(
  name TEXT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS work_author_link(
  id INTEGER PRIMARY KEY,
  work_id INTEGER REFERENCES work(id),
  author_name TEXT REFERENCES author(name)
);

CREATE TABLE IF NOT EXISTS work_fandom_link(
  id INTEGER PRIMARY KEY,
  work_id INTEGER REFERENCES work(id),
  fandom_name TEXT REFERENCES fandom(name)
);

CREATE TABLE IF NOT EXISTS series_author_link(
  id INTEGER PRIMARY KEY,
  series_id INTEGER REFERENCES series(id),
  author_name TEXT REFERENCES author(name)
);

CREATE TABLE IF NOT EXISTS series_work_link(
  id INTEGER PRIMARY KEY,
  series_id INTEGER REFERENCES series(id),
  work_id INTEGER REFERENCES work(id),
  part INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS series_fandom_link(
  id INTEGER PRIMARY KEY,
  series_id INTEGER REFERENCES series(id),
  fandom_name TEXT REFERENCES fandom(name)
);

CREATE TABLE IF NOT EXISTS device_work_link(
  id INTEGER PRIMARY KEY,
  device_name TEXT REFERENCES device(name),
  work_id INTEGER REFERENCES work(id),
  work_last_updated TEXT NOT NULL
);