#!/usr/bin/python
import sys
import socket
import pickle
from cStringIO import StringIO
import time
from timeit import Timer
import re
import subprocess

from PlanningProblemConstants import *
from PlanningProblemJob import *

#Socket parameters
HOST = "131.185.231.182"
PORT = 50005
BUFFER_SIZE = 4096

#Regex to find plan
PLAN_SYNTAX = "\d+\.*\d*: \([0-9A-Za-z\-\_ ]+\)  \[\d+\.*\d*]"
PLAN_REGEX = re.compile(PLAN_SYNTAX)

def processProblem(job):
	#Open files for logging
	bufsize = 0
	log = open(job.logFile, "a+", bufsize)
	plan = open(job.planFile, "a", bufsize)

	#Setup experiment
	reps=1
	call_args = """['%s'], stdout=stdout, stderr=stderr"""%(job.plannerCommand)
	#Run Experiment
	log.write("===%s: Processing %s on %s===\n"%(time.
		strftime("%d %m %Y - %H:%M:%S"), job.problemName, socket.gethostname()))
	log.write("===with Command %s===\n" %job.plannerCommand)
	t = Timer(stmt = """subprocess.call(%s, shell=True)"""%call_args, 
		setup="""import subprocess; stdout=open(\"%s\", 'a'); stderr=stdout"""%job.logFile)
	timeTaken = t.timeit(reps)
	#Write Time Taken to Log
	log.write("\n\n===TIME TAKEN===\n")
	log.write("%f seconds\n"%timeTaken)
	log.write("===EOF===")
	
	#Reset file pointer to read
	log.seek(0,0)
	#Output Plan
	matches = [PLAN_REGEX.findall(line) for line in log]
	for m in matches:
		if len(m) > 0:
			plan.write("%s\n"%m[0])
	plan.close()		

	#Validate the plan
	call_args = """['%s'], stdout=stdout, stderr=stderr"""%(job.validatorCommand)
	subprocess.call(call_args, shell=True, stdout=log, stderr=log)
	log.close()

def shutdownSocket(aSocket):
	aSocket.shutdown(socket.SHUT_RDWR)
	aSocket.close()
	time.sleep(1)

def main(args):
	_id = getInstanceID()

	while True:
		#create an INET, STREAMing socket
		clientsocket = socket.socket(
	   	socket.AF_INET, socket.SOCK_STREAM)
		clientsocket.setsockopt(socket.SOL_SOCKET, 
			socket.SO_REUSEADDR, 1)
		#bind the socket to a public host,
		# and a well-known port
		clientsocket.connect((HOST, PORT))
		msg = getMessageString(_id, REQUEST_PROBLEM)
		clientsocket.sendall(msg)

		data = clientsocket.recv(BUFFER_SIZE)
		reply = getMessage(data)

		#Check if the buffer is empty
		if reply.message == EXIT_PROCESS:
			msg = getMessageString(_id, "Ack. Exiting...")
			conn.sendall(msg)
			shutdownSocket(clientsocket)
			sys.exit(0)

		job = reply.message
		print "Received %s for processing on iteration %i from server id %i"%(job.problemName, 
			job.itr, reply._id)
		processProblem(job)
		clientsocket.close()

#Run Main Function
if __name__ == "__main__":
	main(sys.argv)