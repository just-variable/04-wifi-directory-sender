import json
import os
import socket
from rich.progress import Progress, SpinnerColumn, DownloadColumn, TransferSpeedColumn
import hashlib

BUFFER_SIZE = 64*1024

s = socket.socket()
totalFilesSize = {'value': 0}

def fixName(str):
    if(len(str) > 33):
        str = str[:30] + "..."
    return str + " "*(36-len(str))

def readDir(relPath):
    dirDict = {}
    filesList = os.scandir(relPath)

    for itemObj in filesList:
        itemName = itemObj.name
        if (itemName == os.path.basename(__file__) or itemName == "functions.py" or itemName == "sender2.py"):
            continue
        if (itemObj.is_file()):
            size = os.stat(relPath + itemName).st_size
            totalFilesSize['value'] += size
            thisFile = [itemName, size, "", relPath]
            dirDict[thisFile[0]] = thisFile
        else:
            dirDict[itemName] = readDir(relPath + itemName + "/")
    return dirDict

def sendDir(dirDict, progress, task):
    allmsg= ""
    for itemName in dirDict.keys():
        skip=0
        if (isinstance(dirDict[itemName], list)):
            while (True):
                allmsg += s.recv(BUFFER_SIZE).decode()
                if(("fileSkip:!"+dirDict[itemName][3]+itemName+"!") in allmsg):
                    skip = 1
                    break
                if(("fileGet:!"+dirDict[itemName][3]+itemName+"!") in allmsg):
                    skip = 0
                    break
            if(skip == 1):
                progress.update(task, description=("[green]"+fixName("Skipped: "+itemName)), advance=dirDict[itemName][1])
                continue
            filee = open(dirDict[itemName][3] + itemName, "rb")
            sha256 = hashlib.sha256()

            while True:
                data = filee.read(BUFFER_SIZE*10)
                s.sendall(data)
                sha256.update(data)
                progress.update(task, description=("[red]"+fixName(itemName)), advance=len(data))
                if not data:
                    break

            s.send(b"<END>")
            s.send(b"<HBEGIN>" + bytes("{0}".format(sha256.hexdigest()), "utf-8") + b"<HEND>")

            while (s.recv(BUFFER_SIZE).decode() != ("fileTransfer:" + itemName)):
                print("[+] Waiting for receiver...")
        else:
            sendDir(dirDict[itemName], progress, task)

def main():

    print("[+] Reading files and subdirectories.")
    completeFiles = readDir("./")
    print("[+] Done: Reading files and subdirectories.")

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
        with Progress(SpinnerColumn(), *Progress.get_default_columns(), TransferSpeedColumn(), DownloadColumn()) as progress:
            task = progress.add_task("[red]", total=totalFilesSize['value'])
            sendDir(completeFiles, progress, task)
    
main()
print("\n[+] Done, closing connection...")
s.close()
print("[+] Connection closed.")
input("[-] press enter...")