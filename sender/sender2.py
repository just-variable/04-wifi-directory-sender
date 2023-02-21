import socket
import os
import json
import hashlib

class item:
    def __init__(self, name, size, digest, relPath, dirlist):
        self.name = name
        self.size = size
        self.digest = digest
        self.relPath = relPath
        self.dirlist = dirlist

def readDir(relPath, isSub = 0):
    if(not isSub):
        print("reading directory: " + relPath)
    else:
        print("reading subdirectory: " + relPath)
    dirDict = {}
    filesList = os.scandir(relPath)
    for fileObj in filesList:
        file = fileObj.name
        if (file == os.path.basename(__file__)):
            continue
        if (fileObj.is_file()):
            print("read file: " + file)
            fileDict = 0
            sha256_hash = hashlib.sha256()
            with open(str(relPath + file),"rb") as f:
                for byte_block in iter(lambda: f.read(4096),b""):
                    sha256_hash.update(byte_block)
            fileDigest = sha256_hash.hexdigest()
        else:
            fileDict = readDir(relPath + file + "/", True)
            fileDigest = ""
        thisFile = item(file, os.stat(relPath + file).st_size, fileDigest, relPath + file + "/", fileDict)
        
        if (fileObj.is_file()):
            dirDict[thisFile.name] = thisFile
        else:
            dirDict[thisFile.name] = fileDict #Change later from thisFile.name => thisFile
    return dirDict

print("Reading files and subdirectories...")
completeFiles = readDir("./")
print(str(completeFiles))

s = socket.socket()
port = 5000
BUFFER_SIZE = 4096

s.connect(("localhost", port))
print("Connected.")

completeFilesBytes = str(completeFiles).encode()


s.send(completeFilesBytes)
s.send(b"<END>")

recv = s.recv(BUFFER_SIZE).decode()
if recv == "fileDictTransfer":
    print("File data delivered.\nStarting to send...\n")
    
    for file in completeFiles.keys():
        if (type(completeFiles[file]) != dict):
            filee = open(completeFiles[file].relPath, "rb")
            s.sendall(filee.read())
            s.send(b"<END>")
        
    
    
    # for file in completeFiles.keys():
    #     print("sending: " + file)
    #     filee = open(file, "rb")
    #     s.sendall(filee.read())
    #     s.send(b"<END>")
    #     while (s.recv(BUFFER_SIZE).decode() != "fileTransfer"):
    #         print("Waiting for receiver...")
    #     print("delivered: " + file)

s.close()
input("Hit enter")