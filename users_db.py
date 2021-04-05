import sqlite3


class DatabaseManager:
    DB_PATH = "default_database.db"

    def __init__(self, db_path=None):
        if db_path is not None:
            self.conn = sqlite3.connect(db_path, check_same_thread=False)
        else:
            self.conn = sqlite3.connect(self.DB_PATH, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def create_table(self, query):
        self.cursor.execute(query)
        self.conn.commit()

    def insert_item(self, query, payload):
        self.cursor.execute(query, payload)
        self.conn.commit()

    def get_items_list(self, query):
        self.cursor.execute(query)
        items_list = []
        [items_list.append(item[0]) for item in self.cursor.fetchall()]
        return items_list

    def get_item(self, query, item):
        self.cursor.execute(query + f"'{item}'")
        return self.cursor.fetchone()[0]

    def db_close(self):
        self.conn.close()


class SocketsAppDBManager(DatabaseManager):
    QUERIES = {"create users table": "CREATE TABLE if not exists users (username text PRIMARY KEY, password text)",
               "create user": "INSERT INTO users(username, password) VALUES(?, ?)",
               "get users list": "SELECT username FROM users",
               "get user password": f"SELECT password FROM users WHERE username="}
