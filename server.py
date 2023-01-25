#  coding: utf-8 
import socketserver
from pathlib import Path
# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
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
        print("REACHED HERE")
        data = self.data.decode('utf-8')
        method = data.split(' ')[0]
        errCode = ''
        contentType = ''
        
        if method == "GET":
            path = data.split(' ')[1].split(' ')[0]
            print(method,path)
            if path == '/':
                path = '/index.html'
            buff = ''
            try:

                print("PATH IS: " + path)
                
                if '.' not in path:
                    p = Path('www' + path)
                    # HANDLE DIRECTORIES
                    if p.is_dir():
                        if path[-1] != '/':
                            errCode = "301 Moved Permanently"
                            self.request.sendall(bytearray("HTTP/1.1 {errCode}\nHost:localhost:8000\nLocation:{path}+/\n\n",'utf-8')) 
                            return
                        else:
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
                    with open("www" +path,'r') as f:
                        buff = f.read()
                    errCode = '200 OK'   
                    if path.split('.')[1] == 'html':
                        contentType = 'text/html'
                    elif path.split('.')[1] == 'css':
                        contentType = 'text/css'
            except IsADirectoryError:
                print("DIRECTORY ERROR")
                #self.request.sendall(bytearray("404 Not Found",'utf-8'))
                errCode = '301 Moved Permanently'
            except FileNotFoundError:
                print("FILE NOT FOUND")
                errCode = '404 Not Found'
                #self.request.sendall(bytearray("404 Not Found",'utf-8'))

            header = f"HTTP/1.1 {errCode}\nHost:localhost:8000\nContent-type:{contentType}\n\n"
            self.request.sendall(bytearray((header + buff),'utf-8')) 
        else:
            self.request.sendall(bytearray("HTTP/1.1 405 Method Not Allowed\n\n",'utf-8'))
       
        
        #self.request.sendall(bytearray("200 OK",'utf-8'))


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
