import socket
import threading

ADDRESS = "127.0.0.1"
PORT = 5050


class SocketClient:
    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    FORMAT = "utf-8"

    def start_client(self):
        self.client.connect((self.address, self.port))
        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()
        send_thread = threading.Thread(target=self.send)
        send_thread.start()

    def receive(self):
        while True:
            message = self.client.recv(2048).decode(self.FORMAT)
            print(message)
            if not message:
                self.client.close()
                break

    def send(self):
        while True:
            message = input('')
            self.client.send(message.encode(self.FORMAT))
            if message == "/exit":
                self.client.close()
                break


new_client = SocketClient(ADDRESS, PORT)
new_client.start_client()
