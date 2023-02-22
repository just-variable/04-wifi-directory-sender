import socket
import json
import os
import tqdm

BUFFER_SIZE = 4096

def getDir(dirDict):
    
    for item in dirDict.keys():
        if(isinstance(dirDict[item], list)):
            try:
                os.makedirs(dirDict[item][3])
            except:
                print("", end="")
            
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
                else:
                    fileBytes += data_buffer
            fileBytes = fileBytes.replace(b"<END>", b"")
            file = open(dirDict[item][3] + item, "wb")
            file.write(fileBytes)
            file.close()
        else:
            getDir(dirDict[item])
            
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
port = 5000
s.bind(("localhost", port))
s.listen(5)
print("Listening...")
client, addr = s.accept()
print('Connected to: ', addr)

done = False
dirDictString = ""
while not done:
    data = client.recv(BUFFER_SIZE).decode()
    if("<END>" in data):
        print("Received directory data, receiving files...")
        done = True
        dirDictString += data[:-5]
    else:
        dirDictString += data

client.send(b"dirDictTransfer")
dirDict = json.loads(dirDictString)

getDir(dirDict)
        
print("Done, closing connection...")
client.close()
print("Connection closed.")
input("press enter...")
