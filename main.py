import os
import socket
import tqdm

SEPARATOR = "<SEPARATOR>"
# ASK FOR PATH
path = ""
BUFFER_SIZE = 4096


# Get IP Address over Wifi
ipAddrWifi = os.popen('ipconfig').read()
ipAddrWifi = ipAddrWifi[ipAddrWifi.index("Wi-Fi:"):]
ipAddrWifi = ipAddrWifi[ipAddrWifi.index("IPv4 Address. . . . . . . . . . . : "):ipAddrWifi.index("Subnet Mask")]
ipAddrWifi = ipAddrWifi[ipAddrWifi.index(" : ")+3:]

# Get IP Address over Hotspot
ipAddrHS = os.popen('ipconfig').read()
ipAddrHS = ipAddrHS[ipAddrHS.index("Connection-specific DNS Suffix  . :"):]
ipAddrHS = ipAddrHS[ipAddrHS.index("IPv4 Address. . . . . . . . . . . : "):ipAddrHS.index("Subnet Mask")]
ipAddrHS = ipAddrHS[ipAddrHS.index(" : ")+3:]

print(ipAddrWifi)
print(ipAddrHS)


