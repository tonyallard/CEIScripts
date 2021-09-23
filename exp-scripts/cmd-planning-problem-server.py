#!/usr/bin/python3
import sys
import socket
import time

from PlanningProblemConstants import *
from PlanningProblemJob import *

#Socket Parameters
HOST = socket.gethostname()
PORT = 50005
BUFFER_SIZE = 8192

_id = getInstanceID()

while True:
	print ("What would you like to do?")
	print ("\t 1: Query problem queue size")
	print ("\t 2: Pause Workers")
	print ("\t 3: Resume Workers")
	print ("\t 4: Restrict Workers to %i"%RESTRICTED_WORKER_NUMBER)
	print ("\t 5: Unrestrict Workers")
	print ("\t 6: Request a problem")
	print ("\t 7: Request Current Allocation")
	print ("\t 8: Terminate server")
	print ("\t 9: Terminate workers")
	print ("\t 0: Exit")

	cmd = input("Your choice: ")
	if cmd == "1": #Query problem queue size
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
		printMessage("Received: %s, from machine with id %i"%(reply.message, 
			reply._id))
		clientsocket.close()
	elif cmd == "2": #Pause Workers
		#create an INET, STREAMing socket
		clientsocket = socket.socket(
		   	socket.AF_INET, socket.SOCK_STREAM)
		#bind the socket to a public host,
		# and a well-known port
		clientsocket.connect((HOST, PORT))
		msg = getMessageString(_id, PAUSE_WORKERS)
		clientsocket.sendall(msg)
		
		data = clientsocket.recv(BUFFER_SIZE)
		reply = getMessage(data)
		printMessage("Received: %s, from machine with id %i"%(reply.message, 
			reply._id))
		clientsocket.close()
	elif cmd == "3": #Resume Workers
		#create an INET, STREAMing socket
		clientsocket = socket.socket(
		   	socket.AF_INET, socket.SOCK_STREAM)
		#bind the socket to a public host,
		# and a well-known port
		clientsocket.connect((HOST, PORT))
		msg = getMessageString(_id, RESUME_WORKERS)
		clientsocket.sendall(msg)
		
		data = clientsocket.recv(BUFFER_SIZE)
		reply = getMessage(data)
		printMessage("Received: %s, from machine with id %i"%(reply.message, 
			reply._id))
		clientsocket.close()
	elif cmd == "4": #Restrict Workers
		#create an INET, STREAMing socket
		clientsocket = socket.socket(
		   	socket.AF_INET, socket.SOCK_STREAM)
		#bind the socket to a public host,
		# and a well-known port
		clientsocket.connect((HOST, PORT))
		msg = getMessageString(_id, RESTRICT_WORKERS)
		clientsocket.sendall(msg)
		
		data = clientsocket.recv(BUFFER_SIZE)
		reply = getMessage(data)
		job = reply.message
		printMessage("Received: %s, from machine with id %i"%(reply.message, 
			reply._id))
		clientsocket.close()

	elif cmd == "5": #Unrestrict Workers
		#create an INET, STREAMing socket
		clientsocket = socket.socket(
		   	socket.AF_INET, socket.SOCK_STREAM)
		#bind the socket to a public host,
		# and a well-known port
		clientsocket.connect((HOST, PORT))
		msg = getMessageString(_id, UNRESTRICT_WORKERS)
		clientsocket.sendall(msg)
		
		data = clientsocket.recv(BUFFER_SIZE)
		reply = getMessage(data)
		printMessage("Received: %s, from machine with id %i"%(reply.message, 
			reply._id))
		clientsocket.close()
	elif cmd == "6": #Request a Problem
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
		printMessage("Received: %s for iteration %i from machine with id %i."%(job.problemName, 
			job.itr, reply._id))
		clientsocket.close()

	elif cmd == "7": #Request a Current Allocation
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
		clientsocket.close()
		printMessage("Received Current Allocation from machine with id %i:\n%s"%(reply._id,
			reply.message))

	elif cmd == "8": #Terminate server
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
		printMessage("Received: %s from machine with ID %i"%(reply.message, 
			reply._id))
		clientsocket.close()
		time.sleep(1)
		sys.exit(0)

	elif cmd == "9": #Terminate Workers
		#create an INET, STREAMing socket
		clientsocket = socket.socket(
   		socket.AF_INET, socket.SOCK_STREAM)
		#bind the socket to a public host,
		# and a well-known port
		clientsocket.connect((HOST, PORT))

		msg = getMessageString(_id, TERMINATE_WORKERS)
		clientsocket.sendall(msg)

		data = clientsocket.recv(BUFFER_SIZE)
		reply = getMessage(data)
		printMessage("Received: %s from machine with ID %i"%(reply.message, 
			reply._id))
		clientsocket.close()

	elif cmd == "0": #Exit
		sys.exit(0)
		
	else:
		print ("Error: %s is not a valid option"%cmd)
