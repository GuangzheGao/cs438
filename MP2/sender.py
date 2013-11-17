import argparse
import datetime
import json
import matplotlib.pyplot as plt
import math
import numpy
import socket
import sys
import time

MSS = 100.0
MAX_SEG_COUNT = 25
# Three state of TCP
SLOW_START = 0
CONGESTION_AVOIDANCE = 1
FAST_RECOVERY = 2
DEBUG = False

def formatLog(log):
    if not DEBUG:
        return
    time_str = datetime.datetime.now().strftime("%H:%M:%S.%f")
    print time_str + ': '+log

class TCPSender(object):
    def __init__(self, host, port):
        self.addr = (host, port)
        self.seq = 0
        self.ack = 0
        self.state = SLOW_START
        self.ssthresh = 1000 # slow start threshold
        self.cwnd = MSS # number of MSS of congestion wind, would be 1 at start and timeout
        self.expect_acks = []
        self.dupACKcount = 0
        self.FastRetran = False
        self.TimeOut = False
        self.TimeOutInterval = -1
        self.Throughput = -1
        # socket init
        for res in socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_DGRAM): #UDP
            af, socktype, proto, canonname, sa = res
            try:
                self.socket = socket.socket(af, socktype, proto)
            except socket.error as msg:
                self.socket = None
                continue
            break

        if self.socket is None:
            print 'cant not establish socket connection'
            sys.exit(1)
        
    def send(self, data):
        data_size = len(data)
        start_byte = 0 # the start byte for sending

        last_ack = -1 # last ack received, for duplicated check
        sampleRTT = 0
        eRTT = -1
        devRTT = 0
        self.TimeOutInterval = -1
        elapsed = 2.0
        start = time.time()
        ack_time = 0

        # All just tracking staff
        tracef = open('trace', 'w+')
        tracef.write('')
        tracef.close()
        tracef = open('trace', 'a')

        cwndf = open('cwnd', 'w+')
        cwndf.write('')
        cwndf.close()
        cwndf = open('cwnd', 'a')

        start_time = time.time() # time to send package
        while self.ack < data_size:
            # Keep sending segments until the whole file is sent.
            # All TCP logic is implemented here.
           
            ########################################
            # Sending Logic, send all segs in cwnd #
            ########################################
            for i in xrange(int(self.cwnd / MSS)):
                if self.TimeOut or self.FastRetran:
                    formatLog("Ready to Retransmit Seg: " + str(self.expect_acks[0]))
                    segment = data[self.expect_acks[0]: self.expect_acks[0]+int(MSS)]
                    if len(self.expect_acks) <= 1:
                        _ack = 0
                    else:
                        _ack = self.expect_acks[1]

                    # time the RRT
                    start = time.time()
                    self.socket.sendto(json.dumps({'seg':self.expect_acks[0], 'size':data_size ,'data':segment}), self.addr)
                    elapsed = time.time() - start

                    self.TimeOut = False
                    self.FastRetran = False
                elif len(self.expect_acks) >= min(MAX_SEG_COUNT, self.cwnd / MSS) or self.ack >= data_size or start_byte >= data_size:
                    break
                else:
                    end_byte = start_byte + int(MSS)
                    segment = data[start_byte:end_byte]
                    formatLog("Ready to Transmit New Seg: " + str(start_byte))

                    start = time.time()
                    self.socket.sendto(json.dumps({'seg': start_byte, 'size': data_size, 'data': segment}), self.addr)
                    elapsed = time.time() - start

                    self.expect_acks.append(start_byte)
                    start_byte = end_byte

            # TIMEOUT vals
            if eRTT == -1:
                eRTT = elapsed
            if self.TimeOutInterval == -1:
                self.TimeOutInterval = elapsed*2
            #################
            # Receive Logic #
            #################
            if self.dupACKcount < 3:
                self.socket.settimeout(self.TimeOutInterval)
            try:
                self.ack = int(self.socket.recvfrom(20)[0])
                ack_time = time.time()
                if self.ack >= data_size:
                    break
            except socket.timeout:
                formatLog("Timeout Occured!")
                self.TimeOut = True
                self.state = SLOW_START
                self.ssthresh = (self.cwnd) / 2
                self.cwnd = MSS
                cwndf.write(str(time.time()-start_time)+' '+str(self.cwnd)+'\n')
                self.dupACKcount = 0
                self.TimeOutInterval = self.TimeOutInterval * 2

            if last_ack == -1:
                last_ack = self.ack
                self.expect_acks = [x for x in self.expect_acks if x >= self.ack]
            elif self.ack == last_ack:
                formatLog("Duplicated ACK Received from Receiver: "+ str(self.ack) + ', Duplicated ' + str(self.dupACKcount + 1) + ' times total.')
                # duplicated ack
                self.dupACKcount = self.dupACKcount + 1
                if self.state == FAST_RECOVERY:
                    self.cwnd = self.cwnd + MSS
                    cwndf.write(str(time.time()-start_time)+' '+str(self.cwnd)+'\n')
            else:
                # new ack
                # insert a record to trace
                formatLog("New ACK Received from Receiver: "+ str(self.ack))
                tracef.write(str(ack_time-start_time)+' '+str(self.ack)+'\n')

                last_ack = self.ack
                self.dupACKcount = 0
                self.expect_acks = [x for x in self.expect_acks if x >= self.ack]


                if self.state == SLOW_START:
                    self.cwnd = self.cwnd + MSS
                    cwndf.write(str(time.time()-start_time)+' '+str(self.cwnd)+'\n')
                    if self.cwnd >= self.ssthresh:
                        self.state = CONGESTION_AVOIDANCE
                        continue
                elif self.state == CONGESTION_AVOIDANCE:
                    self.cwnd = (self.cwnd + MSS * (MSS/self.cwnd))
                    cwndf.write(str(time.time()-start_time)+' '+str(self.cwnd)+'\n')
                else:
                    # FAST RECOVERY
                    self.state  = CONGESTION_AVOIDANCE
                    self.cwnd = self.ssthresh
                    cwndf.write(str(time.time()-start_time)+' '+str(self.cwnd)+'\n')

                # Calculate TIMEOUTINTERVAL
                sampleRTT = time.time() - start
                eRTT = 0.875*eRTT+0.175*sampleRTT
                devRTT = 0.25*abs(eRTT-sampleRTT) + 0.75*devRTT
                self.TimeOutInterval = 4*devRTT + eRTT

            if self.dupACKcount >= 3 and self.state is not FAST_RECOVERY:
                self.state = FAST_RECOVERY
                self.FastRetran = True
                self.ssthresh = self.cwnd / 2
                self.cwnd = self.ssthresh + 3*MSS
                cwndf.write(str(time.time()-start_time)+' '+str(self.cwnd)+'\n')
            if not DEBUG:
                continue
            print "============status=========="
            print "state:", self.state
            print "cwnd:", self.cwnd
            print "ssthresh", self.ssthresh
            print "excepted acks:", self.expect_acks
            print "sampleRTT", sampleRTT
            print "eRTT", eRTT
            print "devRTT", devRTT
            print "TimeOutInterval", self.TimeOutInterval
            print "===========end=============="
        cwndf.close()
        tracef.close()

def plotToFile(ftype, fname):
    x_list = []
    y_list = []
    if ftype == 'throughput':
        with open('trace') as f:
            data = f.read()
            data_list = data.split("\n")
            start_time = float(data_list[0].split()[0])
            end_time = float(data_list[-2].split()[0])
            start_ack = float(data_list[0].split()[1])
            end_ack = float(data_list[-2].split()[1])
            tp = (end_ack- start_ack)/(end_time-start_time) * 8
        # print fname+' '+str(tp)+'\n'
        with open('throughput', 'a+') as f:
            f.write(fname+' '+str(tp)+'\n')
        return

    with open(ftype) as f:
        data = f.read()
        data_list = data.split("\n")
        # print data_list
        for line in data_list:
            #print line.split()
            if len(line.split()) > 1:
                x_list.append(line.split(' ')[0])
                y_list.append(line.split(' ')[1])
    #print x_list
    #print y_list
    plt.plot(x_list, y_list, 'or')
    x_list = []
    y_list = []
    plt.savefig(fname)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="the name of file transferred.")
    parser.add_argument("domain", help="domain name of the host running the receiver")
    parser.add_argument("port", type=int, help="upd port that the receiver will receive on")
    parser.add_argument("-t", "--throughput", help="plot throughput", default=False, action="store_true")
    args = parser.parse_args()
    with open(args.filename) as f:
        data = f.read()
    print "--------------------------------------------------"
    sender = TCPSender(args.domain, args.port)
    sender.send(data)
    # pilot trace
    if not args.throughput:
        plt.figure(0)
        plotToFile('trace','trace_' + str(args.port) + '.jpg')
        plt.figure(1)
        plotToFile('cwnd','cwnd_' + str(args.port) + '.jpg')
    else:
        plotToFile('throughput', str(args.port % 100))