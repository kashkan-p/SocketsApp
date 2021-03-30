import socket
import threading

PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
HEADER = 64
FORMAT = "utf-8"
DISCONNECT_MSG = "!disconnect"


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)


def handle_client(connection, address):
    print(f"{address} connected")
    connected = True
    while connected:
        msg_length = connection.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = connection.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT_MSG:
                connected = False
                print(f"[{address}]: disconnected")
            print(f"[{address}]: {msg}")
    connection.close()


def start():
    server.listen()
    print("Server started")
    while True:
        connection, address = server.accept()
        thread = threading.Thread(target=handle_client,
                                  args=(connection, address))
        thread.start()
        print(f"Active connections: {threading.activeCount() - 1}")


start()