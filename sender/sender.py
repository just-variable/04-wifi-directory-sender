import os
import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect(("localhost", 9999))

fileName = "dummy1.zip"

file = open(fileName, "rb")
file_size = os.path.getsize(fileName)

client.send(fileName.encode())
client.send(str(file_size).encode())

client.sendall(file.read())
client.send(b"<END>")

file.close()
client.close()


