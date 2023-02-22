import socket
import json

from modules import client, BUFFER_SIZE, getDir

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
