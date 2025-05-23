"""Simple TCP server"""

from socket import AF_INET, SOCK_STREAM, socket
from threading import Thread

IP = "0.0.0.0"
PORT = 9998


def main():
    """Main function of the server, binds to the IP and PORT and starts the server"""
    server = socket(AF_INET, SOCK_STREAM)
    server.bind((IP, PORT))
    server.listen(5)
    print(f"[*] Listening on {IP}:{PORT}")
    # handler loop of the server, it sends each incoming connection
    # to a separate thread to be handled
    while True:
        client, address = server.accept()
        print(f"[*] Accepted connection from {address[0]}:{address[1]}")
        client_handler = Thread(target=handle_client, args=(client,))
        client_handler.start()


def handle_client(client_socket: socket):
    """
    function to handle request from the client connected, receives data
    from the client and sends example acknowledgement string back to
    the client"""
    with client_socket as sock:
        request = sock.recv(4096)
        print(f'[*] Received: {request.decode("utf-8")}')
        sock.send(b"ACK")


if __name__ == "__main__":
    main()
