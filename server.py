#  coding: utf-8 
import socketserver
from pathlib import Path
import re
# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# Copyright 2023 Jacob Gerun
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)
        #print("REACHED HERE")
        data = self.data.decode('utf-8')
        method = data.split(' ')[0]
        errCode = ''
        contentType = ''
        
        if method == "GET":
            path = data.split(' ')[1].split(' ')[0]
            #print(method,path)
            if path == '/':
                path = '/index.html'
            buff = ''

            #print("PATH IS: " + path)
            # isFile = False
            # temp = path if path[-1] == '/' else path + '/'
            # isFile = True if '.' in temp.split('/')[-2] else False
            p = Path('www' + path)
            #print("Before is_file: " + path)
            if p.exists():
                
                # HANDLE DIRECTORIES
                #print("Before is_dir")
                if p.is_dir():
                    #print("IN is_dir")
                    if shouldGaurd(path):
                        self.request.sendall(bytearray("HTTP/1.1 404 Not Found\n\n",'utf-8'))
                        return
                    #print("VROOM VROOM" + path[-1])
                    if path[-1] != '/':
                        errCode = "301 Moved Permanently"
                        #print("VROOM VROOM")
                        self.request.sendall(bytearray(f"HTTP/1.1 {errCode}\nHost:localhost:8000\nLocation:{path}/\n\n",'utf-8')) 
                        return
                    else:
                        
                        dirIndex = Path("www" + path + 'index.html')
                        #print('DIR INDEX PATH: ' + "www" + path + 'index.html')
                        if dirIndex.is_file():
                            with open("www" + path + 'index.html','r') as f:
                                buff = f.read()
                            errCode = '200 OK'
                            contentType = 'text/html'
                            header = f"HTTP/1.1 {errCode}\nHost:localhost:8000\nContent-type:{contentType}\n\n"
                            self.request.sendall(bytearray((header + buff),'utf-8'))
                        else:
                            self.request.sendall(bytearray("HTTP/1.1 404 Not Found\n\n",'utf-8'))
                            return
                else:
                    if shouldGaurd(path):
                        self.request.sendall(bytearray("HTTP/1.1 404 Not Found\n\n",'utf-8'))
                        return                   
                    try:
                        with open("www" +path,'r') as f:
                            buff = f.read()
                        errCode = '200 OK'   
                        if path.split('.')[1] == 'html':
                            contentType = 'text/html'
                        elif path.split('.')[1] == 'css':
                            contentType = 'text/css'
                        else :                        
                            contentType = 'text/plain'
                    except FileNotFoundError:
                        #print("FILE NOT FOUND")
                        errCode = '404 Not Found'
                        #]=self.request.sendall(bytearray("404 Not Found",'utf-8'))
                    header = f"HTTP/1.1 {errCode}\nHost:localhost:8000\nContent-type:{contentType}\n\n"
                    self.request.sendall(bytearray((header + buff),'utf-8'))
                    return 
            else:
                self.request.sendall(bytearray("HTTP/1.1 404 Not Found\n\n",'utf-8'))
        else:
            self.request.sendall(bytearray("HTTP/1.1 405 Method Not Allowed\n\n",'utf-8'))
       
        
        #self.request.sendall(bytearray("200 OK",'utf-8'))

def shouldGaurd(path):
    #print("GUARD PATTERN",path.count("/.."),"dir count",(path.count("/")/2) - path.count("/.."))
    if path.count("/..") > (path.count("/")/2) - path.count("/.."):
        return True
    return False
if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
