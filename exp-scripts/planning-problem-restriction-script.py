#!/usr/bin/python3
import sys
import argparse
import socket
from datetime import datetime, time
import time as t

'''
Run with crontab with following
01 6,20 * * 1-5	/path/to/planning-problem-restriction-script.py >> /path/to/worker_restriction.log
'''

from PlanningProblemConstants import *

#Socket parameters
DEFAULT_HOST = socket.gethostname()
DEFAULT_PORT = 50005
BUFFER_SIZE = 4096

def shutdownSocket(clientsocket):
	clientsocket.shutdown(socket.SHUT_RDWR)
	clientsocket.close()
	t.sleep(1)

def openSocket(server, port):
	clientsocket = socket.socket(
		   	socket.AF_INET, socket.SOCK_STREAM)
	#Connect
	clientsocket.connect((server, port))
	return clientsocket

def setRestriction(_id, clientsocket, restriction):
	msg = getMessageString(_id, restriction)
	clientsocket.sendall(msg)

def main(args):
	
	parser = argparse.ArgumentParser(description='A script to control number of workers processing depending on the day of week and time of day.')
	parser.add_argument('server',
						metavar='127.0.0.1',
						nargs="?",
						default=DEFAULT_HOST,
						type=str,
						help='The IP address of the experimentation server')
	parser.add_argument('port',
						metavar='50005',
						nargs="?",
						default=DEFAULT_PORT,
						type=int,
						help='The port that the experimentation server is listening on')
	args = parser.parse_args()

	server = args.server
	port = args.port
	
	_id = getInstanceID()
	printMessage("Started. My ID is %i"%_id)

	clientsocket = openSocket(server, port)

	now = datetime.now()
	now_time = now.time()

	if now_time >= time(6,00) and \
		now_time <= time(20,00) and \
		0 <= now.weekday() <= 4: #Restrict Workers
		printMessage("Instructing server at %s:%s to restrict workers"%(server, port))
		setRestriction(_id, clientsocket, RESTRICT_WORKERS)
		
	else: #Unrestrict Workers
		printMessage("Instructing server at %s:%s to set workers free"%(server, port))
		setRestriction(_id, clientsocket, UNRESTRICT_WORKERS)

	data = clientsocket.recv(BUFFER_SIZE)
	reply = getMessage(data)
	job = reply.message
	printMessage("Received: %s, from machine with id %i"%(reply.message, 
		reply._id))

	shutdownSocket(clientsocket)

#Run Main Function
if __name__ == "__main__":
	main(sys.argv)