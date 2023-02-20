import os
import socket
import time
import json

def sendFile(file_name):
    file = open(file_name, "rb")
    file_size = os.path.getsize(file_name)
    time.sleep(5)
    client.send(f"{file_name}-{file_size}".encode())

    client.sendall(file.read())
    client.send(b"<END>")

    file.close()
    # client.close()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

filesList = os.listdir("./")

fileDict = {}
for file in filesList:
        fileDict[file] = os.stat(file).st_size

client.connect(("localhost", 5000))
print("Connected.")

fileDictBytes = json.dumps(fileDict).encode()

client.send(fileDictBytes)
print("Sent file data.")
    
# for f in filesList:
    # sendFile(f)
    
client.close()

