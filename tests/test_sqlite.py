# import sqlite3

# def main():
#     with open('database_setup.sql', 'r') as sql_file:
#         sql_script = sql_file.read()
#     db = sqlite3.connect(":memory:")
#     cursor = db.cursor()
#     cursor.executescript(sql_script)
#     cursor.execute("INSERT INTO work VALUES (123456, \"test title\", \"time\")")
#     data = cursor.execute("SELECT * FROM work").fetchall()
#     print(data)

import unittest
import mock
from AO3LS import ao3

class sqlite_test(unittest.TestCase):

    def test_map(self):
        self.assertEqual(1, 1)
        


if __name__ == '__main__':
    unittest.main()