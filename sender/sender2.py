import json

from modules import readDir, sendDir, BUFFER_SIZE, s

# 0 name, 1 size, 2 digest, 3 relPath, 4 dirlist


port = 5000


print("Reading files and subdirectories...")
completeFiles = readDir("./")

print("Waiting for receiver...")
while True:
    try:
        s.connect(("localhost", port))
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