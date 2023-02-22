import json
import os
import hashlib
import socket
import ifcfg

BUFFER_SIZE = 4096

print("Getting IP Addresses...")
ifcfgDict = ifcfg.interfaces()

wifi = ifcfgDict["Wireless LAN adapter Wi-Fi"]["inet"]
ethernet = ifcfgDict["Ethernet adapter Ethernet 3"]["inet"]
print("Ethernet IP: " + ethernet)
print("LAN IP: " + wifi)

# choice = ""
# while True:
#     if(choice.lower() == "e"):
#         choice = ethernet
#         break
#     elif(choice.lower() == "w"):
#         choice = wifi
#         break
#     else:
#         choice = input("Use Ethernet or LAN? (E/L): ")
        
# while True:
#     try:
#         port = int(input("Enter port to use (4 digits): "))
#     except:
#         continue
#     if(port > 9999 or port < 1025):
#         continue
#     break



s = socket.socket()

totalFilesNb = 0

def readDir(relPath):
    dirDict = {}
    filesList = os.scandir(relPath)
    totalFilesNb = 0
    for fileObj in filesList:
        file = fileObj.name
        if (file == os.path.basename(__file__) or file == "functions.py" or file == "sender2.py"):
            continue
        if (fileObj.is_file()):
            totalFilesNb += 1
            fileDict = 0
            sha256_hash = hashlib.sha256()
            with open(str(relPath + file),"rb") as f:
                for byte_block in iter(lambda: f.read(4096),b""):
                    sha256_hash.update(byte_block)
            fileDigest = sha256_hash.hexdigest()
        else:
            fileDict = readDir(relPath + file + "/")
            fileDigest = ""
        thisFile = [file, os.stat(relPath + file).st_size, fileDigest, relPath, fileDict]
        
        if (fileObj.is_file()):
            dirDict[thisFile[0]] = thisFile
        else:
            dirDict[thisFile[0]] = fileDict

    return dirDict

def sendDir(dirDict):
    for file in dirDict.keys():
        if (isinstance(dirDict[file], list)):
            filee = open(dirDict[file][3] + file, "rb")
            print("Sending: " + file)
            s.sendall(filee.read())
            s.send(b"<END>")
            while (s.recv(BUFFER_SIZE).decode() != ("fileTransfer:" + file)):
                print("Waiting for receiver...")
        else:
            sendDir(dirDict[file])

# 0 name, 1 size, 2 digest, 3 relPath, 4 dirlist

print("Reading files and subdirectories...")
completeFiles = readDir("./")

# print("Waiting for receiver on: " + choice + ":" + str(port) + "...")
while True:
    try:
        s.connect(("0.0.0.0", 5000))
        break
    except:
        None
print("Connected.")

completeFilesBytes = json.dumps(completeFiles)
completeFiles = json.loads(completeFilesBytes)

s.send(completeFilesBytes.encode())
s.send(b"<END>")

recv = s.recv(BUFFER_SIZE).decode()
if recv == "dirDictTransfer":
    print("Directory data received by peer. Starting to send...")
    sendDir(completeFiles)
        
print("Done, closing connection...")
s.close()
print("Connection closed.")
input("press enter...")