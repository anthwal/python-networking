"""Simple UDP client"""

from socket import AF_INET, SOCK_DGRAM, socket

# can't find a udp server so using local settings

target_host: str = "127.0.0.1"
target_port: int = 9997

# create a socket object with datagram settings
client: socket = socket(AF_INET, SOCK_DGRAM)

# send data to the target host, port
client.sendto(b"AAAABBBBCCCC", (target_host, target_port))

# receive data from the server and deconstruct the data and address received
data, addr = client.recvfrom(4096)

print(data.decode(), addr)

client.close()
