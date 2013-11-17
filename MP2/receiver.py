import argparse
import json
import socket
import sys
import time

recv_wind = 25 #always 25 segments of 100 bytes
MAX_SENDER = 100
MSS = 100
class Receiver(object):
    def __init__(self, port, lossypath):
        #TODO: implement lossypath
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('localhost', port))
        self.sock = sock
        self.expect_seg = []
        self.data_size = -1
        self.buffer = {}
        self.result = None
        self.pattern = lossypath

    def listen(self):
        RSN = 0
        while True:
            #print "----------------------------------------------------"
            #print "-------------------New Turn For Receiver------------"
            RSN = RSN + 1
            data, addr = self.sock.recvfrom(200) # segment buffer size is 100 bytes

            # Implement losspattern
            if int(self.pattern[0]) == 1 and (RSN -1) % int(pattern[1]) == 0:

                #print "segment lost:", RSN
                continue # discard the segment we just received and continue
            elif int(self.pattern[0]) == 2 and str(RSN) in self.pattern[1:]:
                #print "segment lost:", RSN
                continue

            data = json.loads(data) # parse data
            #print "Receiver received from sender Seg Num:", data['seg']

            if self.data_size < 0: # init data_size
                self.data_size = data['size']
                start_byte = 0

                # Init: add the first expected packages, 25 or less
                for i in xrange(25):
                    if start_byte >= self.data_size:
                        break
                    self.expect_seg.append(start_byte)
                    start_byte = start_byte + MSS

            if data['seg'] in self.expect_seg:
                # Remove the expected segment in expected list
                index = self.expect_seg.index(data['seg'])
                del self.expect_seg[index]

                # If it is the first in the list, it means that all data previous to this seg is ready
                # So we can append this seg to result file
                if index == 0:
                    if self.result is not None:
                        self.result = self.result + data['data']
                    else:
                        self.result = data['data']

                    # Check the buffer to see if any seg is ready to be appended to file
                    next_seg = data['seg'] + 100
                    if data['seg'] in self.buffer.keys():
                        del self.buffer[data['seg']]
                    while next_seg in self.buffer.keys():
                        self.result = self.result + self.buffer[next_seg]
                        del self.buffer[next_seg]
                        next_seg = next_seg + 100
                else:
                    # If it's not the first one in expected, only put it in buffer
                    self.buffer[data['seg']] = data['data']

                if start_byte < self.data_size:
                    # After we get one seg out, put a new expected in, if there exists
                    self.expect_seg.append(start_byte)
                    start_byte = start_byte + MSS

            #print "expect seg", self.expect_seg
            #print "data buffer", sorted(self.buffer.keys())


            if len(self.expect_seg) > 0:
                #print "Receiver sent to Sender ACK #", self.expect_seg[0]
                self.sock.sendto(str(self.expect_seg[0]), addr)

            else:
                self.sock.sendto(str(self.data_size), addr)
                return self.result

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("port", type=int, help="UDP port the receiver should receive on")
    parser.add_argument("losspattern", help="file aloows emulation of lossy network")
    args = parser.parse_args()

    with open(args.losspattern) as f:
        data = f.read()
    pattern = data.split()

    recev = Receiver(args.port, pattern) #sys.argv[1] is port num, 2 is a file indicating lossy pattern
    #print pattern[1:]
    recev.listen()
