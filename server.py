import socket
import threading

PORT = 5080
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MSG = "/exit"

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
#
#
# def login(client):
#     pass
#
#
# def send_to_client():
#     pass
#
#
def broadcast(msg):
    for client in clients:
        client.send(msg)


def handle_client(client, address):
    print(f"{address} connected")
    client.send("Please choose command write smth".encode(FORMAT))
    while True:
        msg = client.recv(2048).decode(FORMAT)
        if msg == "/exit":
            client.close()
            print("Client closed")
            break
        print(msg)
        client.send(msg.encode(FORMAT))
        if msg == "/register":
            register(client)
        # elif msg == "/login":
        #     login(client)
        # elif msg == "/exit":
        #     connected = False
        #     print(f"[{address}]: disconnected")
        #     client.send(f"[{address}]: disconnected".encode(FORMAT))
        # print(f"[{address}]: {msg}")
        else:
            broadcast(msg.encode(FORMAT))
        # client.close()


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
