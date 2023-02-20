import socket
import tqdm
import time
import json

def getFile(file_name, file_size):
    file_name, file_size = client.recv(1024).decode().split("-")
    time.sleep(3)
    print(file_name)
    print(file_size)
    file = open(file_name, "wb")
    file_bytes = b""

    progress = tqdm.tqdm(unit="B", unit_scale=True, unit_divisor=1000, total=int(int(file_size)))

    done = False
    while not done:
        data = client.recv(1024)
        if(file_bytes[-5:] == b"<END>"):
            done = True
        else:
            file_bytes += data
        progress.update(1024)
    file.write(file_bytes[:-5])
    file.close()
    
    
def getData():
    fileDictBytes = client.recv(1024).decode()
    fileDict = json.loads(fileDictBytes)
    
    progress = tqdm.tqdm(unit="B", unit_scale=True, unit_divisor=1000, total=int(1024))
    progress.update(1024)
    return fileDict

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("localhost", 5000))

server.listen()
print("Listening...")

client, addr = server.accept()
print("Connected.")

fileDict = getData()
print(str(fileDict))
print("Received filenames and sizes.")


client.close()
server.close()    