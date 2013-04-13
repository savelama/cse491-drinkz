#!/usr/bin/env python
import sys
import socket

s = socket.socket()
host = socket.gethostname()
port = int(sys.argv[1])

print 'connecting...'
s.connect((host, port))
s.send("GET / HTTP/1.0\n\n")
clientData = s.recv(1024)
while clientData != "":
    print clientData
    clientData = s.recv(1024)
print 'done'
s.close()
