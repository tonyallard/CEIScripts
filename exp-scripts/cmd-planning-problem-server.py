#!/usr/bin/python
import sys
import socket
import time

from PlanningProblemConstants import *
from PlanningProblemJob import *

#Socket Parameters
HOST = socket.gethostname()
PORT = 50005
BUFFER_SIZE = 4096

_id = getInstanceID()

while True:
	print "What would you like to do?"
	print "\t 1: Query problem queue size"
	print "\t 2: Request a problem"
	print "\t 3: Request a Current Allocation"
	print "\t 4: Terminate server"
	print "\t 5: Exit"

	cmd = input("Your choice: ")
	if cmd == 1:
		#create an INET, STREAMing socket
		clientsocket = socket.socket(
		   	socket.AF_INET, socket.SOCK_STREAM)
		#bind the socket to a public host,
		# and a well-known port
		clientsocket.connect((HOST, PORT))
		msg = getMessageString(_id, PROBLEM_QUEUE_SIZE)
		clientsocket.sendall(msg)
		
		data = clientsocket.recv(BUFFER_SIZE)
		reply = getMessage(data)
		print "Received: %s, from machine with id %i"%(reply.message, 
			reply._id)
		clientsocket.close()

	elif cmd == 2:
		#create an INET, STREAMing socket
		clientsocket = socket.socket(
		   	socket.AF_INET, socket.SOCK_STREAM)
		#bind the socket to a public host,
		# and a well-known port
		clientsocket.connect((HOST, PORT))
		msg = getMessageString(_id, REQUEST_PROBLEM)
		clientsocket.sendall(msg)
		
		data = clientsocket.recv(BUFFER_SIZE)
		reply = getMessage(data)
		job = reply.message
		print "Received: %s for iteration %i from machine with id %i."%(job.problemName, 
			job.itr, reply._id)
		clientsocket.close()

	elif cmd == 3:
		#create an INET, STREAMing socket
		clientsocket = socket.socket(
		   	socket.AF_INET, socket.SOCK_STREAM)
		#bind the socket to a public host,
		# and a well-known port
		clientsocket.connect((HOST, PORT))
		msg = getMessageString(_id, CURRENT_ALLOCATION)
		clientsocket.sendall(msg)
		
		data = clientsocket.recv(BUFFER_SIZE)
		reply = getMessage(data)
		print "Received Current Allocation from machine with id %i:\n%s"%(reply._id,
			reply.message)
		clientsocket.close()

	elif cmd == 4:
		#create an INET, STREAMing socket
		clientsocket = socket.socket(
   		socket.AF_INET, socket.SOCK_STREAM)
		#bind the socket to a public host,
		# and a well-known port
		clientsocket.connect((HOST, PORT))

		msg = getMessageString(_id, EXIT_PROCESS)
		clientsocket.sendall(msg)

		data = clientsocket.recv(BUFFER_SIZE)
		reply = getMessage(data)
		print "Received: %s from machine with ID %i"%(reply.message, 
			reply._id)
		clientsocket.close()
		time.sleep(1)
		sys.exit(0)

	elif cmd == 5:
		sys.exit(0)