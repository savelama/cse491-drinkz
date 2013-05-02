#! /usr/bin/env python
import random
import socket
import time
import app
from StringIO import StringIO

#Create a socket
s = socket.socket()
host = socket.gethostname()
port = random.randint(8000,9999)
s.bind((host, port))

print 'Starting server on', host, port

d = {}
def my_start_response(s, h, return_id=d):
    d['status'] = s
    d['headers'] = h

app_obj = app.SimpleApp()

# liston
s.listen(5)


#While the server is on
while True:
    c, addr = s.accept()
    print 'Got connection from', addr

    # include the directories that are acceptable for the client to enter
    data = c.recv(1024)

    while "\r\n\r\n" not in data:
        receivedData = c.recv(1024)
        if not receivedData:
            break
        data += receivedData

    if data[:4] == "POST":
        splitLines = data.splitlines()
        if(len(splitLines) < 1):
            print "Error"
            continue
        firstLine = splitLines[0]

        reqType, reqPath, reqProtocol = firstLine.split()

        reqHeader = splitLines[1:]

        # SET ENVIRON VARIABLES
        environ = {}
        environ['PATH_INFO'] = reqPath
        environ['REQUEST_METHOD'] = reqType
        environ['CONTENT_LENGTH'] = len(reqHeader[-1])
        environ['wsgi.input'] = StringIO(reqHeader[-1])

        results = app_obj(environ, my_start_response);

        responseHeaders = []
        for key, value in d['headers']:
            responseHeaders.append(key + ": " + value)

        status = "HTTP/1.0 "
        status += d['status']
        status += "\r\n"

        response = "\r\n".join(responseHeaders) + "\r\n\r\n" + "".join(results)

        c.send(status)
        c.send(response)

    elif data[:3] == "GET":
        status = "HTTP/1.0 "
        environ = {}

        if '/recipes' in data[4:]:
            environ['PATH_INFO'] = '/recipes'
        elif '/inventory' in data[4:]:
            environ['PATH_INFO'] = '/inventory'
        elif '/liquor_types' in data[4:]:
            environ['PATH_INFO'] = '/liquor_types'
        elif '/convert_to_ml' in data[4:]:
            environ['PATH_INFO'] = '/convert_to_ml'
        elif '/add_recipe' in data[4:]:
            environ['PATH_INFO'] = '/add_recipe'
        elif '/add_liquor_type' in data[4:]:
            environ['PATH_INFO'] = '/add_liquor_type'
        elif '/add_to_inventory' in data[4:]:
            environ['PATH_INFO'] = '/add_to_inventory'
        elif '/login_1' in data[4:]:
            environ['PATH_INFO'] = '/login_1'
        elif '/login1_process' in data[4:]:
            environ['PATH_INFO'] = '/login1_process'
        elif '/logout' in data[4:]:
            environ['PATH_INFO'] = '/logout'
        elif '/status' in data[4:]:
            environ['PATH_INFO'] = '/status'
        elif '/' in data[5:]:
            environ['PATH_INFO'] = '/'
        else:
            environ['PATH_INFO'] = '/error'

        #Build up a response
        html = app_obj(environ, my_start_response)
        status += d['status']
        status +='\n'

        #Send response
        c.send(status)
        c.send(html[0])


    else:
        c.send("Incorrect Format")
        c.send("GET /[destination]")

    #close the port
    c.close()
