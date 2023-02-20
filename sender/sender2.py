import socket
import os
import json

s = socket.socket()
port = 5000

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
        print("delivered: " + file)

s.close()