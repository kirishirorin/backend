import psycopg2
from psycopg2.extras import DictCursor


class Database():
    def __init__(self, DATABASE_URL):
        self.conn = psycopg2.connect(DATABASE_URL)

    def show(self):
        query = 'SELECT * FROM rolls;'
        with self.conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query)
            rolls = cursor.fetchall()
            return rolls

    def select(self, id):
        query = 'SELECT * FROM rolls WHERE id = %s;'
        with self.conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query, (id,))
            roll = cursor.fetchone()
            return roll

    def show_last_id(self):
        query = 'SELECT id FROM rolls ORDER BY id DESC LIMIT 1;'
        with self.conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query)
            id = cursor.fetchone()
            return id['id']

    def insert(self, datas):
        query = '''INSERT INTO rolls (length, weight, created_at, deleted_at)
                   VALUES (%s, %s, %s, %s);'''
        with self.conn.cursor() as cursor:
            cursor.execute(query, tuple(datas.values()))
            self.conn.commit()

    def update(self, roll):
        query = 'UPDATE rolls SET deleted_at = %s WHERE id = %s;'
        with self.conn.cursor() as cursor:
            cursor.execute(query, (roll['deleted_at'], roll['id']))
            self.conn.commit()

    def close_conn(self):
        self.conn.close()
