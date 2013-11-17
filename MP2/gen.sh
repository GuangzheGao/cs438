#!/bin/bash

RECEIVER_FILE="receiver.py"
SENDER_FILE="sender.py"
PYTHON="/usr/bin/python"
# call script via the interrupter
echo "script starts"
echo "some cleanup"
rm -rf ./*.jpg
rm -rf ./trace
rm -rf ./cwnd
rm -rf ./throughput
echo "plotting cwnd and trace..."
echo "generating for losspattern 0..."
$PYTHON $RECEIVER_FILE 10000 0 &
$PYTHON $SENDER_FILE size10000.txt localhost 10000
echo "generating for losspattern 1..."
$PYTHON $RECEIVER_FILE 10001 1 &
$PYTHON $SENDER_FILE size10000.txt localhost 10001
echo "generating for losspattern 2..."
$PYTHON $RECEIVER_FILE 10002 2 &
$PYTHON $SENDER_FILE size10000.txt localhost 10002
echo "ploting cwnd and trace end"

echo "plotting throughput..."
echo "generating for losspattern 5..."
$PYTHON $RECEIVER_FILE 10005 5 &
$PYTHON $SENDER_FILE -t size1000.txt localhost 10005
$PYTHON $RECEIVER_FILE 10105 5 &
$PYTHON $SENDER_FILE -t size100000.txt localhost 10105
$PYTHON $RECEIVER_FILE 11005 5 &
$PYTHON $SENDER_FILE -t size1000000.txt localhost 11005
echo "generating for losspattern 10..."
$PYTHON $RECEIVER_FILE 10010 10 &
$PYTHON $SENDER_FILE -t size1000.txt localhost 10010
$PYTHON $RECEIVER_FILE 10110 10 &
$PYTHON $SENDER_FILE -t size100000.txt localhost 10110
$PYTHON $RECEIVER_FILE 11110 10 &
$PYTHON $SENDER_FILE -t size1000000.txt localhost 11110
echo "generating for losspattern 20..."
$PYTHON $RECEIVER_FILE 10020 20 &
$PYTHON $SENDER_FILE -t size1000.txt localhost 10020
$PYTHON $RECEIVER_FILE 10120 20 &
$PYTHON $SENDER_FILE -t size100000.txt localhost 10120
$PYTHON $RECEIVER_FILE 11120 20 &
$PYTHON $SENDER_FILE -t size1000000.txt localhost 11120
echo "ploting throughput end"
cat ./throughput
$PYTHON plot_throughput.py
