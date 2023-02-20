import socket
import os
import tqdm
import json

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
port = 5000
s.bind(("localhost", port))

s.listen(5)  # Now wait for client connection.
print("Listening...")
client, addr = s.accept()  # Establish connection with client.
print('Connected to: ', addr)

done = False
fileDictBytes = ""
while not done:
    data = client.recv(1024).decode()
    if("<END>" in data):
        print("transfer done.\n")
        done = True
        fileDictBytes += data[:-5]
    else:
        print("transferring...")
        fileDictBytes += data

client.send(b"fileDictTransfer")
fileDict = json.loads(fileDictBytes)

for file in fileDict.keys():
    progress = tqdm.tqdm(unit="B", unit_scale=True, unit_divisor=1000, total=int(int(fileDict[file])))
    
    done = False
    fileBytes = b""
    while not done:
        data_buffer = client.recv(1024)
        progress.update(1024)
        if(b"<END>" in data_buffer):
            fileBytes += data_buffer
            client.send("fileTransfer".encode())
            done = True
        else:
            fileBytes += data_buffer
    fileBytes = fileBytes.replace(b"<END>", b"")
    file2 = open(file, "wb")
    file2.write(fileBytes)
    file2.close()
        
print("Closing connection.")
client.close()

# while True:
#     print(str(client.recv(1024).decode()))
#     a = input("Enter the msg:")
#     client.sendall(bytes(a, "ascii"))
