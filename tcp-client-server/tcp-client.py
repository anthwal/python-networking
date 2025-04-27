from socket import AF_INET, SOCK_STREAM, socket

# host and port to connect to
target_host: str = "0.0.0.0"
target_port: int = 9998

# create socket object with the socket module
client: socket = socket(AF_INET, SOCK_STREAM)

# connect to the socket
client.connect((target_host, target_port))

# send some data
client.send(b"Some data from the client\r\nHost: localhost\r\n\r\n")

# receive some data
response: bytes = client.recv(4096)

print("buffer response:\n\n", response)

print("\n\nresponse decoded to utf8:\n\n", response.decode("utf8"))

client.close()
