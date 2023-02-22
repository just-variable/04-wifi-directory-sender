import os
import hashlib
import socket

BUFFER_SIZE = 4096
s = socket.socket()

def readDir(relPath):
    dirDict = {}
    filesList = os.scandir(relPath)
    for fileObj in filesList:
        file = fileObj.name
        if (file == os.path.basename(__file__) or file == "functions.py" or file == "sender2.py"):
            continue
        if (fileObj.is_file()):
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