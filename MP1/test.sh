#!/bin/bash

CLIENT_FILE="client.py"
HOST="localhost"
PORT="4000"
PYTHON="/usr/bin/python"

SETUP_CODE="
'import client
c = client.Client()
c.prepare_socket()"
TEST_FILE="./mp1_test"

# call script via the interrupter
echo "----------TESTING STARTS----------"
echo "----------FUNCTION TESTS----------"
for NUM in $(seq 1 6)
do
    $PYTHON $CLIENT_FILE $HOST $PORT $TEST_FILE$NUM
done
echo "--------FUNCTION TEST ENDS--------"
echo "-----------TIMING STARTS----------"
sleep 2
SIZE=1
for NUM in $(seq 1 6)
do
SIZE=$((10*SIZE))
if [ $NUM -eq 1 ]; then
    R_SIZE=1
else
    R_SIZE=$SIZE
fi
echo "-----------File Size:"$R_SIZE"------------"
$PYTHON -m timeit -n 10 -r 1 -s 'import client
c = client.Client()
c.prepare_socket("'$HOST'",'$PORT')' "c.send_request('./mp1_test"$NUM"')"
sleep 2
done
echo "-----------TIMING ENDS------------"
echo "-----------TESTING ENDS-----------"
