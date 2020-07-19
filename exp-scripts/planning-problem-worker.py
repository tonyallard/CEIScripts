#!/usr/bin/python
import sys
import os
import socket
import pickle
from cStringIO import StringIO
import time
from timeit import Timer
import re
import subprocess
import gzip
import shutil

from PlanningProblemConstants import *
from PlanningProblemJob import *

#Socket parameters
PORT = 50005
BUFFER_SIZE = 4096

COLIN_LIKE_PLANNERS = ["Colin-TRH", "Colin-RPG", "POPF", "Optic", "Optic-SLFRP"]
LPG_PLANNERS = ["lpg-td"]
FD_PLANNERS = ["fd_FF", "fd_blind"]
METRICFF_PLANNERS = ["MetricFF"]
MADAGASCAR_PLANNERS = ["madagascar"]

#Regex to find plan
COLIN_PLAN_SYNTAX = "\d+\.*\d*: \([0-9A-Za-z\-\_ ]+\)  \[\d+\.*\d*\]"
COLIN_PLAN_REGEX = re.compile(COLIN_PLAN_SYNTAX)

LPGTD_PLAN_SYNTAX = "\d+\.*\d*: \([0-9A-Za-z\-_ ]+\) \[[0-9DC;:. ]*\]"
LPGTD_PLAN_REGEX = re.compile(LPGTD_PLAN_SYNTAX)

FD_PLAN_SYNTAX = "[0-9A-Za-z\-\_ ]+ \(1\)"
FD_PLAN_REGEX = re.compile(FD_PLAN_SYNTAX)

METRICFF_PLAN_SYNTAX = "\d+: [0-9A-Za-z\-\_ ]+\n"
METRICFF_PLAN_REGEX = re.compile(METRICFF_PLAN_SYNTAX)

MADAGASCAR_PLAN_SYNTAX = "([0-9A-Za-z\-\_]+\([0-9A-Za-z\-\_\,]+\))+"
MADAGASCAR_PLAN_REGEX = re.compile(MADAGASCAR_PLAN_SYNTAX)

def getPlan(planner, logFile, planFile):
	#Read the plan found
	#Reset file pointer to read
	logFile.seek(0,0)
	#Output Plan
	matches = []
	if planner in COLIN_LIKE_PLANNERS:
		matches = [COLIN_PLAN_REGEX.findall(line) for line in logFile]
	elif planner in LPG_PLANNERS:
		matches = [LPGTD_PLAN_REGEX.findall(line) for line in logFile]
	elif planner in FD_PLANNERS:
		matches = [FD_PLAN_REGEX.findall(line) for line in logFile]
		for m in matches:
			if len(m) > 0:
				m[0] = m[0].replace(" (1)", ")")
				m[0] = "(" + m[0]
	elif planner in METRICFF_PLANNERS:
		matches = [METRICFF_PLAN_REGEX.findall(line) for line in logFile]
		for m in matches:
			if len(m) > 0:
				m[0] = re.sub("\d+: ", "(", m[0])
				m[0] = m[0].replace("\n", ")")
	elif planner in MADAGASCAR_PLANNERS:
		matches = [MADAGASCAR_PLAN_REGEX.findall(line) for line in logFile]
		for m in matches:
			m[:] = [x.replace("(", " ") for x in m]
			m[:] = [x.replace(",", " ") for x in m]
			m[:] = ["(" + x for x in m]			
	else:
		print "Error: Unmatched Planner. Plans not extracted or validated."		
	
	for ms in matches:
		for m in ms:
			planFile.write("%s\n"%m)

def processProblem(job):
	#Open files for logging
	buffSize = 0
	log = open(job.logFile, "a+", buffSize)

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
	log.write("====================\n\n")

	plan = open(job.planFile, "a", buffSize)
	getPlan(job.plannerName, log, plan)
	plan.close()		

	#Validate the plan
	log.write("Plan Validation\n")
	call_args = "%s"%(job.validatorCommand)
	subprocess.call(call_args, shell=True, stdout=log, stderr=log)
	
	log.write("===EOF===")
	log.close()

	#Compress files to save space
	with open(job.logFile, 'rb') as f_in, gzip.open(job.logFile + '.gz', 'wb') as f_out:
		shutil.copyfileobj(f_in, f_out)
		f_in.close()
		f_out.close()
	with open(job.planFile, 'rb') as f_in, gzip.open(job.planFile + '.gz', 'wb') as f_out:
		shutil.copyfileobj(f_in, f_out)
		f_in.close()
		f_out.close()

	#Remove uncompressed files
	os.remove(job.logFile)
	os.remove(job.planFile)

def shutdownSocket(aSocket):
	aSocket.shutdown(socket.SHUT_RDWR)
	aSocket.close()
	time.sleep(1)

def main(args):

	HOST = args[1]

	_id = getInstanceID()
	printMessage("Started. My ID is %i"%_id)
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
			clientsocket.sendall(msg)
			printMessage("Received shutdown message from server id %i"%reply._id)
			shutdownSocket(clientsocket)
			sys.exit(0)
		elif reply.message == WORKER_PAUSED:
			printMessage("Received pause message from server id %i. Trying again in 30 seconds."%reply._id)
			shutdownSocket(clientsocket)
			time.sleep(30)
		else:
			job = reply.message
			printMessage("Received %s for processing on iteration %i with planner %s, from server id %i"%(job.problemName, 
				job.itr, job.plannerName, reply._id))
			processProblem(job)
			shutdownSocket(clientsocket)

#Run Main Function
if __name__ == "__main__":
	main(sys.argv)
