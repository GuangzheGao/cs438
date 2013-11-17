#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Client for MP1

import socket
import sys

class Client(object):
    def prepare_socket(self, host, port):
        for res in socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            try:
                self.socket = socket.socket(af, socktype, proto)
            except socket.error as msg:
                self.socket = None
                continue
            try:
                self.socket.connect(sa)
            except socket.error as msg:
                self.socket.close()
                self.socket = None
                continue
            break

        if self.socket is None:
            sys.exit(1)
    
    def send_request(self, path):
        request = 'GET' + ' ' + path + '\r\n'
        self.socket.sendall(request)
        response = self.socket.recv(8192)
        if response == None or len(response)<18:
            sys.exit(1)
        if (response.split())[1] != '200':
            return response
        received_length = len(response)
        total_length = int(response.split('\n',2)[1].split(':')[1])
        while received_length < total_length:
            response = response + self.socket.recv(8192)
            increased_length = len(response)
            if received_length == increased_length:
                sys.exit(1)
            else:
                received_length = increased_length

        #print "real response length:", len(response)
        return response
    
    def request(self, host, port, path):
        self.prepare_socket(host, port)
        return self.send_request(path)

if __name__ == '__main__':
    # get response
    client = Client()
    response = client.request(sys.argv[1], sys.argv[2], sys.argv[3])

    print response
