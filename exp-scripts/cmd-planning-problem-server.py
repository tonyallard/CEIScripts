#!/usr/bin/python
import sys
import socket
import time

from PlanningProblemConstants import *

#Socket Parameters
HOST = socket.gethostname()
PORT = 50005
BUFFER_SIZE = 4096

while True:
	print "What would you like to do?"
	print "\t 1: Query problem queue size"
	print "\t 2: Terminate server"
	print "\t 3: Exit"

	cmd = input("Your choice: ")
	if cmd == 1:
		#create an INET, STREAMing socket
		clientsocket = socket.socket(
		   	socket.AF_INET, socket.SOCK_STREAM)
		#bind the socket to a public host,
		# and a well-known port
		clientsocket.connect((HOST, PORT))

		clientsocket.send(PROBLEM_QUEUE_SIZE)
		data = clientsocket.recv(BUFFER_SIZE)
		print "Received: %s"%data
		clientsocket.close()
	elif cmd == 2:
		#create an INET, STREAMing socket
		clientsocket = socket.socket(
   		socket.AF_INET, socket.SOCK_STREAM)
		#bind the socket to a public host,
		# and a well-known port
		clientsocket.connect((HOST, PORT))

		clientsocket.send(EXIT_PROCESS)
		data = clientsocket.recv(BUFFER_SIZE)
		print "Received: %s"%data
		clientsocket.close()
		time.sleep(1)
		sys.exit(0)
	elif cmd == 3:
		sys.exit(0)