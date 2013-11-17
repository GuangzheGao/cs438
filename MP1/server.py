#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket
import threading
import sys

HOST = 'localhost'
PORT = 4000
MAX_CLIENTS = 100
class ServerThread(threading.Thread):
    def __init__(self, conn):
        threading.Thread.__init__(self)
        self.conn = conn

    def run(self):
        print self.getName()
        while 1:
            request = self.conn.recv(1024)
            if not request: sys.exit(1)
            method, path = request[0:len(request)-2].split(' ')
            if method != 'GET' or request[-2:] != '\r\n':
                response = 'HTTP 400 Bad Request\r\n\r\n'
            else:
                try:
                    with open(path, 'r') as f:
                        response = f.read()
                        response = 'HTTP 200 OK\nContent-Length:'+str(len(response))+'\r\n'+response
                    f.closed
                except IOError:
                    response = 'HTTP 404 Not Found\r\n\r\n'
            self.conn.sendall(response)
        self.conn.close()

if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(MAX_CLIENTS)
    while True:
        conn, addr = s.accept()
        ServerThread(conn).start() 
