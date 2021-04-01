import socket
import threading
import re
from datetime import datetime

DATE_FORM = "%d/%m/%Y %H:%M:%S"
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = "utf-8"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

clients = []
nicknames = []


def register(client):
    print("New connection")
    client.send('Enter your nickname: '.encode(FORMAT))
    nickname = client.recv(1024).decode(FORMAT)
    nicknames.append(nickname)
    clients.append(client)
    print("Nickname is {}".format(nickname))
    broadcast("{} joined!".format(nickname).encode(FORMAT))
    client.send('Connected to server!'.encode(FORMAT))


def login(client):
    pass


def send_to_client(msg):
    addr_nick = re.search(r"(?<=@).*?(?=:)", msg).group(0)
    clients[nicknames.index(addr_nick)].send(msg.encode(FORMAT))


def broadcast(msg):
    for client in clients:
        client.send(msg)


def handle_client(client, address):
    print(f"{address} connected")
    client.send("Please choose command /register /login /exit".encode(FORMAT))
    while True:
        msg = client.recv(2048).decode(FORMAT)
        if msg == "/register":
            register(client)
        elif msg == "/exit":
            client.close()
            print("Client closed")
            break
        elif msg.startswith("@"):
            send_to_client(msg)
        else:
            try:
                print(
                    f"[{datetime.now().strftime(DATE_FORM)}] {nicknames[clients.index(client)]}:-> {msg}")
                broadcast(
                    f"[{datetime.now().strftime(DATE_FORM)}] {nicknames[clients.index(client)]}:-> {msg}".encode(
                        FORMAT))
            except:
                client.send(
                    "Only registered users can post. If you are registered try "
                    "/login".encode(
                        FORMAT))


def start():
    server.listen()
    print("Server started")
    while True:
        client, address = server.accept()
        thread = threading.Thread(target=handle_client,
                                  args=(client, address))
        thread.start()
        print(f"Active connections: {threading.activeCount() - 1}")


start()
