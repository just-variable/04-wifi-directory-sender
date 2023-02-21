import socket
import os
import json
import hashlib


# 0 name, 1 size, 2 digest, 3 relPath, 4 dirlist


def readDir(relPath, isSub = 0):
    if(not isSub):
        print("reading directory: " + relPath)
    else:
        print("reading subdirectory: " + relPath)
    dirDict = {}
    filesList = os.scandir(relPath)
    for fileObj in filesList:
        file = fileObj.name
        if (file == os.path.basename(__file__) or file == "functions.py"):
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
        thisFile = [file, os.stat(relPath + file).st_size, fileDigest, relPath, fileDict]
        
        if (fileObj.is_file()):
            dirDict[thisFile[0]] = thisFile
        else:
            dirDict[thisFile[0]] = fileDict #Change later from thisFile.name => thisFile
    return dirDict

def sendDir(dirDict):

        for file in dirDict.keys():
            if (isinstance(dirDict[file], list)):
                filee = open(dirDict[file][3] + file, "rb")
                print("Sending: " + file)
                s.sendall(filee.read())
                print("Sent: " + file)
                s.send(b"<END>")
                while (s.recv(BUFFER_SIZE).decode() != ("fileTransfer:" + file)):
                    print("Waiting for receiver...")
                print("fileTransfer:" + file)
            else:
                sendDir(dirDict[file])

print("Reading files and subdirectories...")
completeFiles = readDir("./")
print(str(completeFiles))

s = socket.socket()
port = 5000
BUFFER_SIZE = 4096

s.connect(("localhost", port))
print("Connected.")

completeFilesBytes = json.dumps(completeFiles)
completeFiles = json.loads(completeFilesBytes)


s.send(completeFilesBytes.encode())
s.send(b"<END>")

recv = s.recv(BUFFER_SIZE).decode()
print("Waiting for dirDictTransfer message...")

if recv == "dirDictTransfer":
    print("File data delivered.\nStarting to send...\n")
    
    sendDir(completeFiles)
        
print("Done. Closing...")
    
    # for file in completeFiles.keys():
    #     print("sending: " + file)
    #     filee = open(file, "rb")
    #     s.sendall(filee.read())
    #     s.send(b"<END>")
    #     while (s.recv(BUFFER_SIZE).decode() != "fileTransfer"):
    #         print("Waiting for receiver...")
    #     print("delivered: " + file)

s.close()
print("Closed.")