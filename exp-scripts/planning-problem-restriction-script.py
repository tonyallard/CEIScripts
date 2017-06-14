#!/usr/bin/python
import sys
import socket
from datetime import datetime, time
import time as t

from PlanningProblemConstants import *

#Socket parameters
HOST = socket.gethostname()
PORT = 50005
BUFFER_SIZE = 4096

def shutdownSocket(aSocket):
	aSocket.shutdown(socket.SHUT_RDWR)
	aSocket.close()
	t.sleep(1)

def main(args):
	_id = getInstanceID()
	print "Started. My ID is %i"%_id

	now = datetime.now()
	now_time = now.time()

	clientsocket = socket.socket(
		   	socket.AF_INET, socket.SOCK_STREAM)
	#bind the socket to a public host,
	# and a well-known port
	clientsocket.connect((HOST, PORT))

	if now_time >= time(06,00) and \
		now_time <= time(19,30) and \
		0 <= now.weekday() <= 4: #Restrict Workers
		print "Instructing server at %s to restrict workers"%HOST
		msg = getMessageString(_id, RESTRICT_WORKERS)
		clientsocket.sendall(msg)
		
	else: #Unrestrict Workers
		print "Instructing server at %s to set workers free"%HOST
		msg = getMessageString(_id, UNRESTRICT_WORKERS)
		clientsocket.sendall(msg)

	data = clientsocket.recv(BUFFER_SIZE)
	reply = getMessage(data)
	job = reply.message
	print "Received: %s, from machine with id %i"%(reply.message, 
		reply._id)
	shutdownSocket(clientsocket)

#Run Main Function
if __name__ == "__main__":
	main(sys.argv)