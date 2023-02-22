import json
import os
import math
import socket
from rich.progress import Progress
# 0 name, 1 size, 2 digest, 3 relPath, 4 dirlist
BUFFER_SIZE = 1024*1024

# print("Getting IP Addresses...")
# ifcfgDict = ifcfg.interfaces()

# wifi = ifcfgDict["Wireless LAN adapter Wi-Fi"]["inet"]
# ethernet = ifcfgDict["Ethernet adapter Ethernet 3"]["inet"]
# print("Ethernet IP: " + ethernet)
# print("LAN IP: " + wifi)


s = socket.socket()
totalFilesSize = {'value': 0}
def readDir(relPath):
    dirDict = {}
    filesList = os.scandir(relPath)
    for fileObj in filesList:
        file = fileObj.name
        if (file == os.path.basename(__file__) or file == "functions.py" or file == "sender2.py"):
            continue
        if (fileObj.is_file()):
            fileDict = 0
            # sha256_hash = hashlib.sha256()
            # with open(str(relPath + file),"rb") as f:
            #     for byte_block in iter(lambda: f.read(4096),b""):
            #         sha256_hash.update(byte_block)
            # fileDigest = sha256_hash.hexdigest()
            fileDigest = ""
        else:
            fileDict = readDir(relPath + file + "/")
            fileDigest = ""
        size = os.stat(relPath + file).st_size
        totalFilesSize['value'] += size
        thisFile = [file, size, fileDigest, relPath, fileDict]
        
        if (fileObj.is_file()):
            dirDict[thisFile[0]] = thisFile
        else:
            dirDict[thisFile[0]] = fileDict

    return dirDict

def sendDir(dirDict, progress):
    for file in dirDict.keys():
        if (isinstance(dirDict[file], list)):
            filee = open(dirDict[file][3] + file, "rb")
            nameWithSpaces = ""
            if(len(file) > 33):
                nameWithSpaces = file[:30] + "..."
            else:
                nameWithSpaces = file
            nameWithSpaces = nameWithSpaces + " "*(36-len(nameWithSpaces))
            if(dirDict[file][1]>52428800):
                while True:
                    data = filee.read(52428800)
                    s.send(data)
                    progress.update(task1, advance=52428800)
                    if not data:
                        break
            else:
                s.sendall(filee.read())
                progress.update(task1, description=("[red]"+nameWithSpaces), advance=dirDict[file][1])
            s.send(b"<END>")
            while (s.recv(BUFFER_SIZE).decode() != ("fileTransfer:" + file)):
                print("[+] Waiting for receiver...")
        else:
            sendDir(dirDict[file], progress)

print("[+] Reading files and subdirectories...")
completeFiles = readDir("./")

receiverIP = input("[-] Enter IP of receiver or leave blank for localhost: ")
if (receiverIP == ""):
    receiverIP = "localhost"
s.connect((receiverIP, 5000))
print("[+] Connected.")

completeFilesBytes = json.dumps(completeFiles)
completeFiles = json.loads(completeFilesBytes)

s.send(completeFilesBytes.encode())
s.send(b"<END>")

recv = s.recv(BUFFER_SIZE).decode()
if recv == "dirDictTransfer":
    print("[+] Directory data received by peer. Starting to send...\n")
    with Progress() as progress:
        task1 = progress.add_task("[red]", total=totalFilesSize['value'])
        sendDir(completeFiles, progress)
    
        
print("\n[+] Done, closing connection...")
s.close()
print("[+] Connection closed.")
input("[-] press enter...")