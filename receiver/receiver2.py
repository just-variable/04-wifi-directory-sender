import socket
import json
import os
import ifcfg
from rich.progress import Progress, DownloadColumn, SpinnerColumn, BarColumn, TransferSpeedColumn, TextColumn, TimeRemainingColumn, TimeElapsedColumn

BUFFER_SIZE = 2*1024*1024

def getDir(dirDict):
    for item in dirDict.keys():
        if(isinstance(dirDict[item], list)):
            try:
                os.makedirs(dirDict[item][3])
            except:
                None

            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), TimeElapsedColumn(), BarColumn(), TimeRemainingColumn(),  TransferSpeedColumn(), DownloadColumn(True)) as progress:
                
                nameWithSpaces = ""
                if(len(item) > 33):
                    nameWithSpaces = item[:30] + "..."
                else:
                    nameWithSpaces = item
                nameWithSpaces = nameWithSpaces + " "*(36-len(nameWithSpaces))
                task1 = progress.add_task("[cyan]" + nameWithSpaces, total=dirDict[item][1])

                done = False
                fileBytes = b""
                
                if(dirDict[item][1] > 52428800):
                    counter = 0
                    while not done:
                        data_buffer = client.recv(BUFFER_SIZE)
                        counter += BUFFER_SIZE/52428800
                        if(b"<END>" in data_buffer):
                            progress.update(task1, advance=len(data_buffer)-5)
                            fileBytes += data_buffer
                            client.send(("fileTransfer:" + item).encode())
                            done = True
                            fileBytes = fileBytes.replace(b"<END>", b"")
                            file = open(dirDict[item][3] + item, "wb")
                            file.write(fileBytes)
                            file.close()
                        else:
                            progress.update(task1, advance=len(data_buffer))
                            fileBytes += data_buffer
                            if(counter > 0.95):
                                file = open(dirDict[item][3] + item, "wb")
                                file.write(fileBytes)
                                counter = 0
                                
                                
                else:
                    while not done:
                        data_buffer = client.recv(BUFFER_SIZE)
                        if(b"<END>" in data_buffer):
                            progress.update(task1, advance=len(data_buffer)-5)
                            fileBytes += data_buffer
                            client.send(("fileTransfer:" + item).encode())
                            done = True
                        else:
                            progress.update(task1, advance=len(data_buffer))
                            fileBytes += data_buffer
                        fileBytes = fileBytes.replace(b"<END>", b"")
                        file = open(dirDict[item][3] + item, "wb")
                        file.write(fileBytes)
                        file.close()
        else:
            getDir(dirDict[item])
            
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

print("[+] Getting IP Addresses...")
ifcfgDict = ifcfg.interfaces()

for adapter in ifcfgDict.keys():
    try:
        print("[*] " + adapter + ": " + ifcfgDict[adapter]["inet"])
    except:
        continue

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
        
print("\n[+] Done, closing connection...")
client.close()
input("[-] press enter...")
