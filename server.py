#!/usr/bin/python3
#  coding: utf-8 
import socketserver

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

HOST, PORT = "localhost", 8080
root_dir = 'www'

mime_types = {
        'html': 'text/html',
        'css' : 'text/css',
        'binary': 'application/octet-stream'
}


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        request = parse_http_request(self.data.decode('utf-8'))

        if request['method'].upper() != 'GET':
            # TODO: Abstract with errno variable
            self.request.sendall(bytearray('HTTP/1.1 405 Method Not Allowed', 'utf-8'))
            return

        header = 'HTTP/1.1 200 OK\nContent-Type: '
        filetype = request['file'].split('.')[-1]
        if not filetype.isalpha():  # Check if we should redirect the client
            try:
                host = request['host']
            except KeyError:
                host = f'{HOST}:{PORT}'

            self.request.sendall(bytearray(f"HTTP/1.1 301 Moved Permanently\nLocation: http://{host}{request['file']}/", 'utf-8'))
            return

        if filetype == 'html':
            header += mime_types['html']
        elif filetype == 'css':
            header += mime_types['css']
        else:
            header += mime_types['binary']

        try:
            requested_file = open(f"{root_dir}{request['file']}")
        except FileNotFoundError:
            self.request.sendall(bytearray('HTTP/1.1 404 Not Found', 'utf-8'))
            return

        self.request.sendall(bytearray('{}\n\n{}'.format(header, requested_file.read()), 'utf-8'))


def parse_http_request(request_str: str):
    # '\r\n' may be used for encoding newlines so remove '\r'
    headers = request_str.replace('\r', '').split('\n')  

    # We need only parse the first line since we are not expected to deal with
    # request headers.
    request = {}
    method = headers[0].split(' ')
    request['method'] = method[0]
    request['file'] = method[1].replace('../', '')

    if request['file'][-1] == '/':
        request['file'] += 'index.html'

    for header in headers[1:]:
        if header.startswith('Host:'):
            request['host'] = header.split(' ')[1]
            break;

    return request

def main():
    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return

if __name__ == "__main__":
    main()
