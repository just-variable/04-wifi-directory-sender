import socket
import os
import tqdm
import json
import hashlib

class item:
    def __init__(self, name, size, digest, relPath, dirlist):
        self.name = name
        self.size = size
        self.digest = digest
        self.relPath = relPath
        self.dirlist = dirlist

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
port = 5000
s.bind(("localhost", port))
BUFFER_SIZE = 4096

s.listen(5)  # Now wait for client connection.
print("Listening...")
client, addr = s.accept()  # Establish connection with client.
print('Connected to: ', addr)

done = False
dirDictString = ""
while not done:
    data = client.recv(BUFFER_SIZE).decode()
    if("<END>" in data):
        print("Received: fileData")
        done = True
        dirDictString += data[:-5]
    else:
        print("Receiving: fileData")
        dirDictString += data

client.send(b"dirDictTransfer")
dirDict = json.loads(dirDictString)
print(str(dirDict))


def getDir(dirDict):
    
    for item in dirDict.keys():
        if(isinstance(dirDict[item], list)):
            print("File: " + dirDict[item][3] + item)
            try:
                os.makedirs(dirDict[item][3])
            except:
                print("Directory exists, skipping...")
            
            print("Receiving: " + item)
            progress = tqdm.tqdm(unit="B", unit_scale=True, unit_divisor=1024, total=int(dirDict[item][1]))
            done = False
            fileBytes = b""
            while not done:
                progress.update(BUFFER_SIZE)
                data_buffer = client.recv(BUFFER_SIZE)
                if(b"<END>" in data_buffer):
                    fileBytes += data_buffer
                    client.send(("fileTransfer:" + item).encode())
                    done = True
                    print("Received: " + item)
                else:
                    fileBytes += data_buffer
            fileBytes = fileBytes.replace(b"<END>", b"")
            file = open(dirDict[item][3] + item, "wb")
            file.write(fileBytes)
            file.close()
        else:
            print("Folder: " + item)
            getDir(dirDict[item])
            
    

getDir(dirDict)

# for file in fileDict.keys():
#     print("\nReceiving: " + file)
#     progress = tqdm.tqdm(unit="B", unit_scale=True, unit_divisor=1024, total=int(fileDict[file]))
#     done = False
#     fileBytes = b""
#     while not done:
#         data_buffer = client.recv(BUFFER_SIZE)
#         progress.update(BUFFER_SIZE)
#         if(b"<END>" in data_buffer):
#             fileBytes += data_buffer
#             client.send("fileTransfer".encode())
#             done = True
#             print("Received: " + file)
#         else:
#             fileBytes += data_buffer
#     fileBytes = fileBytes.replace(b"<END>", b"")
#     file2 = open(file, "wb")
#     file2.write(fileBytes)
#     file2.close()
        
print("Closing connection.")
client.close()
# while True:
#     print(str(client.recv(1024).decode()))
#     a = input("Enter the msg:")
#     client.sendall(bytes(a, "ascii"))
