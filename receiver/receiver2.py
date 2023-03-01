import socket
import json
import os
from rich.progress import Progress, DownloadColumn, SpinnerColumn, BarColumn, TransferSpeedColumn, TextColumn, TimeRemainingColumn, TimeElapsedColumn
import re

BUFFER_SIZE = 64*1024



def fixName(str):
    if(len(str) > 33):
        str = str[:30] + "..." 
    return str + " "*(36-len(str))

def getDir(dirDict):
    for itemName in dirDict.keys():
        if(isinstance(dirDict[itemName], list)):
            try:
                os.makedirs(dirDict[itemName][3])
            except:
                None

            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), TimeElapsedColumn(), BarColumn(), TimeRemainingColumn(),  TransferSpeedColumn(), DownloadColumn(True)) as progress:
                task1 = progress.add_task("[cyan]" + fixName(itemName), total=dirDict[itemName][1])
                file = open(dirDict[itemName][3] + itemName, "wb")
                done = False

                while not done:
                    data_buffer = client.recv(BUFFER_SIZE)
                    if all([x in data_buffer for x in [b"<END>", b"<HBEGIN>", b"<HEND>"]]):
                        progress.update(task1, advance=len(data_buffer)-5)
                        sha256 = re.search(b'<HBEGIN>(.*)<HEND>', data_buffer).group(1)
                        print(b"got all tags: " + sha256)
                        data_buffer = data_buffer.replace(b"<END><HBEGIN>"+sha256+b"<HEND>", b"")
                        file.write(data_buffer)

                        dirDict[itemName][2] = str(sha256)
                        client.send(("fileTransfer:" + itemName).encode())
                        done = True

                    elif(b"<END>" in data_buffer and not all([x in data_buffer for x in [b"<HBEGIN>", b"<HEND>"]])):
                        
                        progress.update(task1, advance=len(data_buffer)-5)
                        data = data_buffer
                        data += client.recv(BUFFER_SIZE)
                        sha256 = re.search(b'<HBEGIN>(.*)<HEND>', data).group(1)
                        print(b"got tags seperately: " + sha256)
                        data = data.replace(b"<END><HBEGIN>"+sha256+b"<HEND>", b"")
                        file.write(data)
                        
                        dirDict[itemName][2] = str(sha256)
                        client.send(("fileTransfer:" + itemName).encode())
                        done = True
                    else:
                        progress.update(task1, advance=len(data_buffer))
                        file.write(data_buffer)
                file.close()
        else:
            getDir(dirDict[itemName])
            
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

s.bind(("0.0.0.0", 5000))
s.listen(5)
print("[+] Listening...")
client, addr = s.accept()
print('[+] Connected to: ', addr)

done = False
dirDictString = ""
while not done:
    data = client.recv(BUFFER_SIZE).decode()
    if("<END>" in data):
        print("[+] Received directory data, receiving files...\n")
        done = True
        dirDictString += data[:-5]
    else:
        dirDictString += data

client.send(b"dirDictTransfer")
dirDict = json.loads(dirDictString)

getDir(dirDict)

print(str(dirDict))

print("\n[+] Done, closing connection...")
client.close()
input("[-] press enter...")
