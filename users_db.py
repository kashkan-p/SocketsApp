import sqlite3


class Database:
    def __init__(self, path):
        self.path = path
        self.conn = sqlite3.connect(path)
        self.cursor = self.conn.cursor()

    def create_table(self, table_name):
        self.cursor.execute(f"""CREATE TABLE if not exists {table_name} 
                                (username text PRIMARY KEY, password text)""")
        self.conn.commit()

    def insert_item(self, table_name, payload):
        self.cursor.execute(f"""INSERT INTO {table_name}(username, password) 
                                VALUES(?, ?)""", payload)
        self.conn.commit()

    def get_users_list(self, table_name):
        self.cursor.execute(f"""SELECT username FROM {table_name}""")
        users = []
        [users.append(user[0]) for user in self.cursor.fetchall()]
        return users

    def get_user_password(self, table_name, username):
        self.cursor.execute(f"""SELECT password FROM {table_name} 
                                WHERE username='{username}'""")
        return self.cursor.fetchone()[0]

    def db_close(self):
        self.conn.close()
