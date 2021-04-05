"""This module describes SocketClient class that provides connection to TCP socket messaging server"""
import socket
import threading


class SocketClient:
    """This class provides set up for connection to a TCP messaging server."""
    FORMAT = "utf-8"

    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start_client(self):
        """This method connects client to a server"""
        try:
            self.client.connect((self.address, self.port))
            receive_thread = threading.Thread(target=self.receive)
            receive_thread.start()
            send_thread = threading.Thread(target=self.send)
            send_thread.start()
        except:
            print("The server is unreachable")

    def receive(self):
        """This method receives messages from a server"""
        try:
            while True:
                message = self.client.recv(2048).decode(self.FORMAT)
                print(message)
                if not message:
                    self.client.close()
                    break
        except OSError:
            print("You left the server")

    def send(self):
        """This method sends messages to a server"""
        while True:
            message = input('')
            self.client.send(message.encode(self.FORMAT))
            if message == "/exit":
                self.client.close()
                break


if __name__ == "__main__":
    ADDRESS = "127.0.0.1"
    PORT = 5000

    new_client = SocketClient(ADDRESS, PORT)
    new_client.start_client()
