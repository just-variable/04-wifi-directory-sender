import socket
import os
import tqdm
import json
import hashlib

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
port = 5000
s.bind(("localhost", port))
BUFFER_SIZE = 4096

s.listen(5)  # Now wait for client connection.
print("Listening...")
client, addr = s.accept()  # Establish connection with client.
print('Connected to: ', addr)

done = False
fileDictBytes = ""
while not done:
    data = client.recv(BUFFER_SIZE).decode()
    if("<END>" in data):
        print("Received: fileData")
        done = True
        fileDictBytes += data[:-5]
    else:
        print("Receiving: fileData")
        fileDictBytes += data

client.send(b"fileDictTransfer")
fileDict = eval(fileDictBytes)
# print(str(fileDict))

for file in fileDict.keys():
    print("\nReceiving: " + file)
    progress = tqdm.tqdm(unit="B", unit_scale=True, unit_divisor=1024, total=int(fileDict[file]))
    done = False
    fileBytes = b""
    while not done:
        data_buffer = client.recv(BUFFER_SIZE)
        progress.update(BUFFER_SIZE)
        if(b"<END>" in data_buffer):
            fileBytes += data_buffer
            client.send("fileTransfer".encode())
            done = True
            print("Received: " + file)
        else:
            fileBytes += data_buffer
    fileBytes = fileBytes.replace(b"<END>", b"")
    file2 = open(file, "wb")
    file2.write(fileBytes)
    file2.close()
        
print("Closing connection.")
client.close()
input("Hit enter")
# while True:
#     print(str(client.recv(1024).decode()))
#     a = input("Enter the msg:")
#     client.sendall(bytes(a, "ascii"))
