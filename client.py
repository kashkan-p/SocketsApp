import socket
import threading

PORT = 5050
SERVER = "127.0.1.1"
ADDR = (SERVER, PORT)
FORMAT = "utf-8"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)


def receive():
    while True:
        message = client.recv(2048).decode(FORMAT)
        print(message)
        if not message:
            client.close()
            break


def send():
    while True:
        message = input('')
        client.send(message.encode(FORMAT))
        if message == "/exit":
            client.close()
            break


receive_thread = threading.Thread(target=receive)
receive_thread.start()

send_thread = threading.Thread(target=send)
send_thread.start()
