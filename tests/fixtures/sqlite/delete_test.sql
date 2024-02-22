INSERT INTO work VALUES (123456, "Work 1", "2024-01-02"), (234567, "Work 2", "2024-02-02"), (345678, "Work 3", "2024-02-02");
INSERT INTO fandom VALUES ("Fandom 1"), ("Fandom 2");
INSERT INTO author VALUES ("Author 1"), ("Author 2");
INSERT INTO series VALUES (654321, "Series 1"), (765432, "Series 2");

INSERT INTO work_fandom_link (work_id, fandom_name) VALUES (123456, "Fandom 1"), (234567, "Fandom 1"), (345678, "Fandom 2");
INSERT INTO work_author_link (work_id, author_name) VALUES (123456, "Author 1"), (345678, "Author 1"), (234567, "Author 2");
INSERT INTO series_work_link (series_id, work_id, part) VALUES (654321, 123456, 1), (654321, 234567, 2), (765432, 345678, 1);
INSERT INTO series_fandom_link (series_id, fandom_name) VALUES (654321, "Fandom 1"), (654321, "Fandom 2"), (765432, "Fandom 1"), (765432, "Fandom 2");
INSERT INTO series_author_link (series_id, author_name) VALUES (654321, "Author 1"), (765432, "Author 2");