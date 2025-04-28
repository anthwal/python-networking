"""Simple TCP client"""

from socket import AF_INET, SOCK_STREAM, socket

# host and port to connect to
target_host: str = "www.google.com"
target_port: int = 80

# create socket object with the socket module
client: socket = socket(AF_INET, SOCK_STREAM)

# connect to the socket
client.connect((target_host, target_port))

# send some data
client.send(b"GET  / HTTP/1.1\r\nHost: google.com\r\n\r\n")

# receive some data
response: bytes = client.recv(4096)

print("buffer response:\n\n", response)

print("\n\nresponse decoded to utf8:\n\n", response.decode("utf8"))

client.close()
