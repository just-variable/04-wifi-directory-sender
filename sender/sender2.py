import socket               # Import socket module
import os
import tqdm
import json

s = socket.socket()         # Create a socket object
port = 5000                # Reserve a port for your service.

s.connect(("localhost", port))
print("Connected.")

filesList = os.listdir("./")

fileDict = {}
for file in filesList:
        fileDict[file] = os.stat(file).st_size

fileDictBytes = json.dumps(fileDict).encode()


s.send(fileDictBytes)
s.send(b"<END>")

recv = s.recv(1024).decode()
if recv == "fileDictTransfer":
    print("File data delivered successfully.")
    
    for file in fileDict.keys():
        print("sending: " + file)
        filee = open(file, "rb")
        s.sendall(filee.read())
        s.send(b"<END>")
        while (s.recv(1024).decode() != "fileTransfer"):
            print("Waiting for receiver...")
        print(file + " delivered.")
    
print(str(recv))

s.close()