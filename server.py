import re
import socket
import threading
from datetime import datetime
from logger import logger
from users_db import Database


ADDRESS = "127.0.0.1"
PORT = 5050


class SocketServer:
    def __init__(self, address, port, db_path):
        self.address = address
        self.port = port
        self.db_path = db_path
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients_connected = []
        self.usernames_connected = []

    FORMAT = "utf-8"
    DATE_FORM = "%d/%m/%Y %H:%M:%S"
    WELCOME_MSG = "Welcome to the server. Please, type '/help' to get a list of available commands"
    HELP_MSG = """List of available commands:
                  /register - to register your username and set password
                  /login -  to log in to server if you already 
                            have a registered username
                  /users - to get a list of connected users
                  /exit - to disconnect from the server
                  @<username>: - to send a message to user with a particular 
                                 username (note: colon is required)
                  if you are logged in type anything to command prompt to 
                  broadcast your message to the server and every connected user"""

    def start_server(self):
        self.server.bind((self.address, self.port))
        self.server.listen()
        print("Server started")
        while True:
            client, address = self.server.accept()
            logger.info(f"{address} connected")
            thread = threading.Thread(target=self.handle_client, args=(client, address))
            thread.start()
            print(f"Active connections: {threading.activeCount() - 1}")

    def handle_client(self, client, address):
        print(f"{address} connected")
        client.send(self.WELCOME_MSG.encode(self.FORMAT))
        while True:
            msg = client.recv(2048).decode(self.FORMAT)
            if msg == "/help":
                client.send(self.HELP_MSG.encode(self.FORMAT))
            elif msg == "/register":
                self.register(client, self.db_path)
            elif msg == "/login":
                self.login(client, self.db_path)
            elif msg == "/exit":
                client.close()
                print(f"{address} disconnected")
                break
            elif msg.startswith("@"):
                self.send_to_client(msg)
            else:
                try:
                    print(f"[{datetime.now().strftime(self.DATE_FORM)}]"
                          f" {self.usernames_connected[self.clients_connected.index(client)]}:-> {msg}")
                    self.broadcast(f"[{datetime.now().strftime(self.DATE_FORM)}]"
                                   f" {self.usernames_connected[self.clients_connected.index(client)]}:->"
                                   f" {msg}".encode(self.FORMAT))
                    logger.info(f"{self.usernames_connected[self.clients_connected.index(client)]}"
                                f" sent a broadcast message")
                except:
                    client.send("Only registered users can post. If you are registered try /login".encode(self.FORMAT))

    def register(self, client, db_path):
        db = Database(db_path)
        client.send('Enter your username: '.encode(self.FORMAT))
        username = client.recv(1024).decode(self.FORMAT)
        while username in db.get_users_list("users"):
            client.send("Username is already in use. Try again or /exit".encode(self.FORMAT))
            username = client.recv(1024).decode(self.FORMAT)
        client.send('Enter your password: '.encode(self.FORMAT))
        password = client.recv(1024).decode(self.FORMAT)
        while len(password) < 6:
            client.send("Password too short. It should be at lest 5 symbols".encode(self.FORMAT))
            password = client.recv(1024).decode(self.FORMAT)
        db.insert_item("users", (username, password))
        logger.info(f"New user registered. Username is {username}")
        print(f"New user registered. Username is {username}")
        client.send(f"You successfully registered as {username}. Now /login.".encode(self.FORMAT))

    def login(self, client, db_path):
        db = Database(db_path)
        client.send('Enter your username: '.encode(self.FORMAT))
        username = client.recv(1024).decode(self.FORMAT)
        while username not in db.get_users_list("users"):
            client.send("Wrong username. Try again or use /register or /exit".encode(self.FORMAT))
            username = client.recv(1024).decode(self.FORMAT)
        client.send('Enter your password: '.encode(self.FORMAT))
        password = client.recv(1024).decode(self.FORMAT)
        while password != db.get_user_password("users", username):
            client.send("Password is wrong. Try again or use /exit".encode(self.FORMAT))
            password = client.recv(1024).decode(self.FORMAT)
        self.usernames_connected.append(username)
        self.clients_connected.append(client)
        logger.info(f"{username} logged in")
        client.send(f"You successfully logged in as {username}.".encode(self.FORMAT))

    def send_to_client(self, msg):
        addr_username = re.search(r"(?<=@).*?(?=:)", msg).group(0)
        self.clients_connected[self.usernames_connected.index(addr_username)].send(msg.encode(self.FORMAT))

    def broadcast(self, msg):
        for client in self.clients_connected:
            client.send(msg)


test_base = Database("users_db")
test_base.create_table("users")
new_server = SocketServer(ADDRESS, PORT, "users_db")
new_server.start_server()
