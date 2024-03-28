# test_postgres.py
import unittest
import psycopg2
import os


class TestPostgresConnection(unittest.TestCase):
    def setUp(self):
        self.conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
        )

    def test_connection(self):
        cur = self.conn.cursor()
        cur.execute("SELECT 1")
        self.assertEqual(cur.fetchone()[0], 1)


if __name__ == "__main__":
    unittest.main()
