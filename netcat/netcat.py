"""Simple netcat implementation in Python"""

import argparse
import shlex
import socket
import subprocess
import sys
import textwrap
import threading


def execute(cmd: str) -> str | None:
    """
    executes the command string provided and returns the output string
    """
    cmd = cmd.strip()
    if not cmd:
        return None
    output: bytes | str = subprocess.check_output(
        shlex.split(cmd), stderr=subprocess.STDOUT
    )

    return output.decode()


class NetCat:
    """
    Simple Python implementation of the netcat tool
    """

    def __init__(self, args, buffer=None) -> None:
        self.args = args
        self.buffer = buffer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def run(self):
        """
        Entry point of the program, checks if the program is in listen mode
        """
        if self.args.listen:
            self.listen()
        else:
            self.send()

    def send(self):
        """
        Establishes a connection to a target server and port,
        sends an initial buffer if provided, and
        facilitates bidirectional communication by receiving
        data and allowing user input to send messages
        in an interactive loop.

        Raises:
            KeyboardInterrupt: Captures user termination to ensure cleanup and graceful exit.

        """
        self.socket.connect((self.args.target, self.args.port))
        if self.buffer:
            self.socket.send(self.buffer)

        try:
            while True:
                recv_len = 1
                response = ""
                while recv_len:
                    data = self.socket.recv(4096)
                    recv_len = len(data)
                    response += data.decode()
                    if recv_len < 4096:
                        break
                if response:
                    print(response)
                    buffer = input("> ")
                    buffer += "\n"
                    self.socket.send(buffer.encode())
        except KeyboardInterrupt:
            print("User terminated.")
            self.socket.close()
            sys.exit()

    def listen(self):
        """
        Listens for incoming connection if Program used
        in listen mode
        """
        print("listening")
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5)

        while True:
            client_socket, _ = self.socket.accept()
            client_thread = threading.Thread(target=self.handle, args=(client_socket,))
            client_thread.start()

    def handle(self, client_socket: socket.socket):
        """
        Handler function for incoming types of requests
        which can be either command shell, upload, or execute
        """
        if self.args.execute:
            output = execute(self.args.execute)
            client_socket.send(str(output).encode())

        elif self.args.upload:
            file_buffer = b""
            while True:
                data = client_socket.recv(4096)
                if data:
                    file_buffer += data
                    print(len(file_buffer))
                else:
                    break

            with open(self.args.upload, "wb") as f:
                f.write(file_buffer)
            message = f"Saved file {self.args.upload}"
            client_socket.send(message.encode())

        elif self.args.command:
            cmd_buffer = b""
            while True:
                try:
                    client_socket.send(b"BHP: #> ")
                    while "\n" not in cmd_buffer.decode():
                        cmd_buffer += client_socket.recv(64)
                    response = execute(cmd_buffer.decode())
                    if response:
                        client_socket.send(response.encode())
                    cmd_buffer = b""
                except Exception as e:
                    print(f"server killed {e}")
                    self.socket.close()
                    sys.exit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="BHP Net Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """
        Example:
        netcat.py -t 192.168.1.108 -p 5555 -l -c # command shell
        netcat.py -t 192.168.1.108 -p 5555 -l -u=mytest.txt # upload to file
        netcat.py -t 192.168.1.108 -p 5555 -l -e=\"cat /etc/passwd\" # execute command
        echo 'ABC' | ./netcat.py -t 192.168.1.108 -p 135 # echo text to server port 135
        netcat.py -t 192.168.1.108 -p 5555 # connect to server
        """
        ),
    )
    parser.add_argument(
        "-c", "--command", action="store_true", help="initialize command shell"
    )
    parser.add_argument("-e", "--execute", help="execute specified command")
    parser.add_argument("-l", "--listen", action="store_true", help="listen")
    parser.add_argument("-p", "--port", type=int, default=5555, help="specified port")
    parser.add_argument("-t", "--target", default="192.168.1.203", help="specified IP")
    parser.add_argument("-u", "--upload", help="upload file")
    input_args = parser.parse_args()
    if input_args.listen:
        BUFFER = ""
    else:
        BUFFER = sys.stdin.read()

    nc = NetCat(input_args, BUFFER.encode("utf-8"))
    nc.run()
