import socket
import os
import json
import hashlib

s = socket.socket()
port = 5000
BUFFER_SIZE = 4096

s.connect(("localhost", port))
print("Connected.")

filesList = os.listdir("./")
filesList.remove("sender2.py")

fileDict = {}
for file in filesList:
        fileDict[file] = os.stat(file).st_size

fileDictBytes = json.dumps(fileDict).encode()


s.send(fileDictBytes)
s.send(b"<END>")

recv = s.recv(BUFFER_SIZE).decode()
if recv == "fileDictTransfer":
    print("File data delivered.")
    
    for file in fileDict.keys():
        print("sending: " + file)
        filee = open(file, "rb")
        s.sendall(filee.read())
        s.send(b"<END>")
        while (s.recv(BUFFER_SIZE).decode() != "fileTransfer"):
            print("Waiting for receiver...")
        print("delivered: " + file)

s.close()
input("Hit enter")