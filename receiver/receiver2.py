import socket
import json
import os
import ifcfg
try:
    from rich.progress import Progress, DownloadColumn, SpinnerColumn, BarColumn, TransferSpeedColumn, TextColumn, TimeRemainingColumn, TimeElapsedColumn
except:
    print("[+] Installing modules...")
    os.system("pip install rich")

BUFFER_SIZE = 8*1024

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
                file = open(dirDict[item][3] + item, "wb")
                while not done:
                    data_buffer = client.recv(BUFFER_SIZE)
                    if(b"<END>" in data_buffer):
                        progress.update(task1, advance=len(data_buffer)-5)
                        client.send(("fileTransfer:" + item).encode())
                        data_buffer = data_buffer.replace(b"<END>", b"")
                        file.write(data_buffer)
                        done = True
                    else:
                        progress.update(task1, advance=len(data_buffer))
                        file.write(data_buffer)
                    
                file.close()
        else:
            getDir(dirDict[item])
            
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

# print("[+] Getting IP Addresses...")
# ifcfgDict = ifcfg.interfaces()

# for adapter in ifcfgDict.keys():
#     try:
#         print("[*] " + adapter + ": " + ifcfgDict[adapter]["inet"])
#     except:
#         continue

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
