"""This module describes SocketServer class for TCP socket messaging"""
import logging
import re
import socket
import sys
import threading
from datetime import datetime
from users_db import SocketsAppDBManager

logging.basicConfig(format='%(asctime)s - %(message)s',
                    datefmt='[%d.%m.%Y - %H:%M:%S]',
                    level=logging.INFO)


class SocketServer:
    """This class provides set up for a TCP messaging server."""
    FORMAT = "utf-8"
    DATE_FORM = "%d/%m/%Y %H:%M:%S"
    WELCOME_MSG = "Welcome to the server. Please, type '/help' to get a list of available commands"
    HELP_MSG = """List of available commands:
    /register - to register your username and set password
    /login -  to log in to server if you already have a registered username
    /users - to get a list of connected users
    /exit - to disconnect from the server
    @<username>: - to send a message to user with a particular username (note: colon is required)
    if you are logged in type anything to command prompt to broadcast your message to the server and every connected 
    user"""

    def __init__(self, address, port, db):
        self.address = address
        self.port = port
        self.db = db
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients_connected = []
        self.usernames_connected = []

    def start_server(self):
        """Binds server socket to a particular address and starts listening to connections"""
        self.server.bind((self.address, self.port))
        self.server.listen()
        logging.info(f"The server started on {self.address} {self.port}")
        while True:
            try:
                client, address = self.server.accept()
                logging.info(f"{address} connected")
                logging.info("The server stopped")
                self.server.close()
                thread = threading.Thread(target=self.handle_client, args=(client, address))
                thread.start()
                logging.info(f"Active connections: {threading.activeCount() - 1}")
            except KeyboardInterrupt:
                logging.info("The server stopped")
                self.server.close()
                sys.exit()

    def handle_client(self, client, address):
        """This method provides interaction between server and client"""
        logging.info(f"{address} connected")
        client.send(self.WELCOME_MSG.encode(self.FORMAT))
        while True:
            msg = client.recv(2048).decode(self.FORMAT)
            if msg == "/help":
                client.send(self.HELP_MSG.encode(self.FORMAT))
            elif msg == "/register" and client not in self.clients_connected:
                self.register(client, self.db)
            elif msg == "/login" and client not in self.clients_connected:
                self.login(client, self.db)
            elif msg == "/users":
                client.send(str(self.usernames_connected).encode(self.FORMAT))
            elif msg == "/exit":
                logging.info(f"{address} (user: {self.username(client)}) disconnected")
                self.broadcast(f"{self.username(client)} disconnected".encode(self.FORMAT))
                self.usernames_connected.remove(self.username(client))
                self.clients_connected.pop(self.client_id(client))
                client.close()
                break
            elif msg.startswith("@") and client in self.clients_connected:
                self.send_to_client(client, msg)
            elif not msg:
                logging.info(f"{address} disconnected")
                client.close()
                break
            else:
                try:
                    logging.info(self.message_format(self.current_time(), self.username(client), msg))
                    self.broadcast(
                        self.message_format(self.current_time(), self.username(client), msg).encode(self.FORMAT))
                except:
                    client.send("You can messaging only after you /register or /login".encode(self.FORMAT))

    def register(self, client, db):
        """Method provides registration new users. Writes new usernames and passwords to database"""
        client.send('Enter your username: '.encode(self.FORMAT))
        username = client.recv(1024).decode(self.FORMAT)
        while username in db.get_items_list(db.QUERIES["get users list"]):
            client.send("Username is already in use. Try again or /exit".encode(self.FORMAT))
            username = client.recv(1024).decode(self.FORMAT)
        client.send('Enter your password: '.encode(self.FORMAT))
        password = client.recv(1024).decode(self.FORMAT)
        while len(password) < 6:
            client.send("Password too short. It should be at lest 5 symbols".encode(self.FORMAT))
            password = client.recv(1024).decode(self.FORMAT)
        db.insert_item(db.QUERIES["create user"], (username, password))
        logging.info(f"New user registered. Username is {username}")
        client.send(f"You successfully registered as {username}. Now /login.".encode(self.FORMAT))

    def login(self, client, db):
        """Method provides logging in for registered users"""
        client.send('Enter your username: '.encode(self.FORMAT))
        username = client.recv(1024).decode(self.FORMAT)
        while username not in db.get_items_list(db.QUERIES["get users list"]):
            client.send("Wrong username. Try again or use /register or /exit".encode(self.FORMAT))
            username = client.recv(1024).decode(self.FORMAT)
        client.send('Enter your password: '.encode(self.FORMAT))
        password = client.recv(1024).decode(self.FORMAT)
        while password != db.get_item(db.QUERIES["get user password"], username):
            client.send("Password is wrong. Try again or use /exit".encode(self.FORMAT))
            password = client.recv(1024).decode(self.FORMAT)
        self.usernames_connected.append(username)
        self.clients_connected.append(client)
        logging.info(f"{username} logged in")
        client.send(f"You successfully logged in as {username}.".encode(self.FORMAT))

    def send_to_client(self, client, msg):
        """Method provides client to client messaging"""
        try:
            addr_username = re.search(r"(?<=@).*?(?=:)", msg).group(0)
            if addr_username in self.usernames_connected:
                self.clients_connected[self.usernames_connected.index(addr_username)].send(msg.encode(self.FORMAT))
            else:
                client.send("The user you trying to message is offline".encode(self.FORMAT))
        except:
            client.send("Wrong format of a message".encode(self.FORMAT))

    def broadcast(self, msg):
        """Method provides broadcasting messages to a server and online users"""
        for client in self.clients_connected:
            client.send(msg)

    def current_time(self):
        """Returns current time"""
        return datetime.now().strftime(self.DATE_FORM)

    def username(self, client):
        """Returns username of a current session connection"""
        return self.usernames_connected[self.clients_connected.index(client)]

    def client_id(self, client):
        """Returns ID of a current session connection"""
        return self.clients_connected.index(client)

    @staticmethod
    def message_format(time, user, msg):
        """Formatting messages sent by users"""
        return f"[{time}] {user}:-> {msg}"


if __name__ == "__main__":
    ADDRESS = "127.0.0.1"
    PORT = 5000

    database = SocketsAppDBManager("socket_test.db")
    database.create_table(database.QUERIES["create users table"])
    new_server = SocketServer(ADDRESS, PORT, database)
    new_server.start_server()
