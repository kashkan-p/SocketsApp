"""Module describes base class for interacting with sqlite3 database and set of specific queries for user database"""
import sqlite3


class DatabaseManager:
    """This class provides connection to database and sending queries"""
    def __init__(self, db_path="default_database.db"):
        """Initializes path to database and creates connection and cursor objects"""
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def create_table(self, query):
        """This should method create table in database"""
        self.cursor.execute(query)
        self.conn.commit()

    def insert_item(self, query, payload):
        """This method should insert item with specific into database"""
        self.cursor.execute(query, payload)
        self.conn.commit()

    def get_items_list(self, query):
        """This method should return list of specific items from database"""
        self.cursor.execute(query)
        items_list = []
        [items_list.append(item[0]) for item in self.cursor.fetchall()]
        return items_list

    def get_item(self, query, item):
        """This method should return specific item from database"""
        self.cursor.execute(query + f"'{item}'")
        return self.cursor.fetchone()[0]

    def db_close(self):
        self.conn.close()


class SocketsAppDBManager(DatabaseManager):
    """This class contains specific queries for SocketServer database"""
    QUERIES = {"create users table": "CREATE TABLE if not exists users (username text PRIMARY KEY, password text)",
               "create user": "INSERT INTO users(username, password) VALUES(?, ?)",
               "get users list": "SELECT username FROM users",
               "get user password": f"SELECT password FROM users WHERE username="}
