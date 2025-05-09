"""Simple TCP proxy in Python"""

from socket import AF_INET, SOCK_STREAM, socket
from sys import argv, exit
from threading import Thread

HEX_FILTER: str = "".join(
    [(len(repr(chr(i))) == 3) and chr(i) or "." for i in range(256)]
)


def hexdump(src: bytes | str, length=16, show=True) -> list:
    """
    Generate a hex dump of a given input string or bytes object.

    This function creates a hexadecimal representation of the input with
    a specified length of bytes per line. It also provides a printable
    representation of the content alongside the hex dump. Users can opt
    to display the output directly or return it as a list of strings.

    Parameters:
    src: bytes | str
        The input data to be converted to a hex dump. Can be either
        a 'bytes' object or a string.
    length: int, optional
        The number of bytes to display per line in the hex dump.
        Defaults to 16.
    show: bool, optional
        Determines whether to print the hex dump directly. If set to
        False, the hex dump is returned as a list of strings. Defaults
        to True.

    Returns:
    list
        Returns a list of strings representing the hex dump.

    Raises:
    TypeError
        If `src` is not of type bytes or str.
    """
    if isinstance(src, bytes):
        src = src.decode()
    results = []
    for i in range(0, len(src), length):
        word = str(src[i : i + length])
        printable = word.translate(HEX_FILTER)
        hexa = " ".join([f"{ord(c):02X}" for c in word])
        hexwidth = length * 3
        results.append(f"{i:04x} {hexa:<{hexwidth}} {printable}")
    if show:
        for line in results:
            print(line)
    return results


def receive_from(connection: socket) -> bytes:
    """
    Receives data from a socket connection until no more data is sent or an
    exception is raised. The method assembles all received chunks into a
    single bytes object.

    Args:
        connection (socket): The socket connection to receive data from.

    Returns:
        bytes: The complete data received from the socket connection.
    """
    buffer = b""
    connection.settimeout(10)
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break

            buffer += data

    except Exception as e:
        print("error ", e)

    return buffer


def request_handler(buffer: bytes) -> bytes:
    """
    Handles incoming binary packets, processes the data, and modifies the buffer
    before sending it back.

    This function takes a binary data buffer as input, modifies or processes the
    information contained within, and returns the updated binary buffer as output.

    Args:
        buffer: Binary data to be modified and processed.

    Returns:
        Modified binary buffer after processing.
    """
    # perform packet modifications
    return buffer


def response_handler(buffer: bytes) -> bytes:
    """
    Processes and modifies the response packet data.

    The function takes raw packet data as input, applies any
    modifications required, and returns the modified packet data
    as output.

    Args:
        buffer (bytes): The raw packet data to be processed.

    Returns:
        bytes: The modified packet data.
    """
    # perform packet modifications
    return buffer


def proxy_handler(
    client_socket: socket,
    remote_host: str,
    remote_port: int,
    receive_first: bool,
) -> None:
    """
    Handles the proxy connection by relaying data between a local client and a remote server.

    This function establishes a connection with the remote host and optionally receives data first,
    then continuously transfers data between the local client and the remote server while applying
    custom request and response handlers. The function is designed for bidirectional data transfer
    until one or both connections are closed.

    Parameters:
    client_socket: socket
        The socket representing the local client connection.
    remote_host: str
        The hostname or IP address of the remote server to connect to.
    remote_port: int
        The port number of the remote server.
    receive_first: bool
        A flag indicating whether to receive data from the remote server before starting
        the bidirectional data transfer.

    Returns:
    None
    """
    remote_socket = socket(AF_INET, SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    if receive_first:
        remote_buffer = receive_from(remote_socket)
        if len(remote_buffer):
            print(f"[<==] Received {len(remote_buffer)} bytes from remote.")
            hexdump(remote_buffer)

    while True:
        local_buffer = receive_from(client_socket)
        if len(local_buffer):
            print(f"[<==] Received {len(local_buffer)} bytes from local.")
            hexdump(local_buffer)

            local_buffer = request_handler(local_buffer)
            remote_socket.send(local_buffer)
            print("[==>] Sent to remote.")

        remote_buffer = receive_from(remote_socket)
        if len(remote_buffer):
            print(f"[<==] Received {len(remote_buffer)} bytes from remote.")
            hexdump(remote_buffer)

            remote_buffer = response_handler(remote_buffer)
            client_socket.send(remote_buffer)
            print("[==>] Sent to local.")

        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closing connections.")
            break


def server_loop(
    local_host: str,
    local_port: int,
    remote_host: str,
    remote_port: int,
    receive_first: bool,
):
    """
    Main server loop, binds to the local host and port and starts the server
    """
    server = socket(AF_INET, SOCK_STREAM)
    try:
        server.bind((local_host, local_port))
    except Exception as e:
        print(f"[!!] Failed to listen on {local_host}:{local_port}")
        print("[!!] Check for other listening sockets or correct permissions.")
        print(e)
        exit(0)

    print(f"[*] Listening on {local_host}:{local_port}")
    server.listen(5)
    while True:
        client_socket, addr = server.accept()
        # print out the local connection information
        print(f"> Received incoming connection from {addr[0]}:{addr[1]}")

        proxy_thread = Thread(
            target=proxy_handler,
            args=(client_socket, remote_host, remote_port, receive_first),
        )
        proxy_thread.start()


def main():
    """Main function of the proxy, parses the command line arguments and starts the server"""
    if len(argv[1:]) != 5:
        print("Usage: proxies/proxy.py [localhost] [localport]", end=" ")
        print("[remotehost] [remoteport] [receive_first]")
        print("Example: proxies/proxy.py 127.0.0.1 9000 172.31.134.104 9000 True")
        exit(0)

    local_host = argv[1]
    local_port = int(argv[2])

    remote_host = argv[3]
    remote_port = int(argv[4])

    receive_first = argv[5]

    receive_first = bool(receive_first)

    server_loop(local_host, local_port, remote_host, remote_port, receive_first)


if __name__ == "__main__":
    main()
