#!/usr/bin/python3
import sys
import os
import socket
import argparse
import ipaddress
import time
from timeit import Timer
import re
import subprocess
import gzip
import shutil
from pathlib2 import Path


from PlanningProblemConstants import *
from PlanningProblemJob import *

#Socket parameters
DEFAULT_IP = '127.0.0.1'
DEFAULT_PORT = 50005
BUFFER_SIZE = 8192

#Regex to find plan
COLIN_PLAN_SYNTAX = "\d+\.*\d*:[\s]+\([0-9A-Za-z\-\_ ]+\)[\s]+\[\d+\.*\d*\]"
COLIN_PLAN_REGEX = re.compile(COLIN_PLAN_SYNTAX)

FD_PLAN_SYNTAX = "[0-9A-Za-z\-\_ ]+ \(1\)"
FD_PLAN_REGEX = re.compile(FD_PLAN_SYNTAX)

METRICFF_PLAN_SYNTAX = "\d+: [0-9A-Za-z\-\_ ]+\n"
METRICFF_PLAN_REGEX = re.compile(METRICFF_PLAN_SYNTAX)

MADAGASCAR_PLAN_SYNTAX = "([0-9A-Za-z\-\_]+\([0-9A-Za-z\-\_\,]+\))+"
MADAGASCAR_PLAN_REGEX = re.compile(MADAGASCAR_PLAN_SYNTAX)

def colinPlanFileHandler(logFile, planFileName):
	planFile = open(planFileName, "a")
	#Read the plan found
	#Reset file pointer to read
	logFile.seek(0,0)
	#Output Plan
	matches = [COLIN_PLAN_REGEX.findall(line) for line in logFile]
	for ms in matches:
		for m in ms:
			planFile.write("%s\n"%m)
	planFile.close()

def fdPlanFileHanlder(logFile, planFileName):
	planFile = open(planFileName, "a")
	#Read the plan found
	#Reset file pointer to read
	logFile.seek(0,0)
	#Output Plan
	matches = [FD_PLAN_REGEX.findall(line) for line in logFile]
	for m in matches:
		if len(m) > 0:
			m[0] = m[0].replace(" (1)", ")")
			m[0] = "(" + m[0]

	for ms in matches:
		for m in ms:
			planFile.write("%s\n"%m)
	planFile.close()

def ffPlanFileHandler(logFile, planFileName):
	planFile = open(planFileName, "a")
	#Read the plan found
	#Reset file pointer to read
	logFile.seek(0,0)
	#Output Plan
	matches = [METRICFF_PLAN_REGEX.findall(line) for line in logFile]
	for m in matches:
		if len(m) > 0:
			m[0] = re.sub("\d+: ", "(", m[0])
			m[0] = m[0].replace("\n", ")")

	for ms in matches:
		for m in ms:
			planFile.write("%s\n"%m)
	planFile.close()

def madagascarPlanFileHandler(logFile, planFileName):
	planFile = open(planFileName, "a")
	#Read the plan found
	#Reset file pointer to read
	logFile.seek(0,0)
	#Output Plan
	matches = [MADAGASCAR_PLAN_REGEX.findall(line) for line in logFile]
	for m in matches:
		m[:] = [x.replace("(", " ") for x in m]
		m[:] = [x.replace(",", " ") for x in m]
		m[:] = ["(" + x for x in m]	

	for ms in matches:
		for m in ms:
			planFile.write("%s\n"%m)
	planFile.close()

def lpgtdPlanFileHandler(logFile, planFileName):
	#remove extra plan files as appropriate
	for x in range(1, 3):
		extraFile = "%s_%i.SOL"%(planFile, x)
		extraPlanFilePath = Path(extraFile)
		if extraPlanFilePath.is_file():
			os.remove(extraFile)

def itsatPlanFileHandler(logFile, planFile):
	#Move plan file to match naming convention
	itsat_plan_filename = f"{planFile}.1"
	shutil.move(itsat_plan_filename, planFile)
	#Remove redundant files
	itsat_planx = f"{os.path.splitext(planFile)[0]}.planx"
	itsat_orders = f"{os.path.splitext(planFile)[0]}-orders.txt"
	if Path(itsat_planx).is_file():
			os.remove(itsat_planx)
	if Path(itsat_orders).is_file():
		os.remove(itsat_orders)

PLAN_FILE_HANDLERS = {
	"Colin-TRH-Colin" : colinPlanFileHandler,
	"Popf-TRH-Popf" : colinPlanFileHandler, 
	"Colin-RPG" : colinPlanFileHandler, 
	"POPF-RPG" : colinPlanFileHandler, 
	"Optic-RPG" : colinPlanFileHandler, 
	"Optic-SLFRP" : colinPlanFileHandler, 
	"tplan" : colinPlanFileHandler,
	"tplanS0T0" : colinPlanFileHandler, 
	"tplanS0T1" : colinPlanFileHandler,
	"tplanS1T0" : colinPlanFileHandler,
	"tplanS1T1" : colinPlanFileHandler,
	"tplanS2T0" : colinPlanFileHandler,
	"tplanS2T1" : colinPlanFileHandler,
	"tplanS3T0" : colinPlanFileHandler,
	"tplanS3T1" : colinPlanFileHandler,
	"tplanS4T0" : colinPlanFileHandler,
	"tplanS4T1" : colinPlanFileHandler,
	"tplanS5T0" : colinPlanFileHandler,
	"tplanS5T1" : colinPlanFileHandler,
	"tplanS6T0" : colinPlanFileHandler,
	"tplanS6T1" : colinPlanFileHandler,
	"tplanS7T0" : colinPlanFileHandler,
	"tplanS7T1" : colinPlanFileHandler,
	"fd_FF" : fdPlanFileHanlder,
	"fd_blind" : fdPlanFileHanlder,
	"MetricFF" : ffPlanFileHandler,
	"madagascar" : madagascarPlanFileHandler,
	"lpg-td" : lpgtdPlanFileHandler,
	"itsat" : itsatPlanFileHandler
	}

def processProblem(job):
	#Open files for logging
	log = open(job.logFile, "a+")

	#Setup experiment
	reps=1
	call_args = """['%s'], stdout=stdout, stderr=stderr"""%(job.plannerCommand)
	
	log.write("===%s: Processing %s on %s===\n"%(time.
		strftime("%d %m %Y - %H:%M:%S"), job.problemName, socket.gethostname()))
	log.write("===with Command %s===\n" %job.plannerCommand)
	log.flush()
	
	#Run Experiment
	t = Timer(stmt = """subprocess.call(%s, shell=True)"""%call_args, 
		setup="""import subprocess; stdout=open(\"%s\", 'a'); stderr=stdout"""%job.logFile)
	timeTaken = t.timeit(reps)
	
	#Write Time Taken to Log
	log.write("\n\n===TIME TAKEN===\n")
	log.write("%f seconds\n"%timeTaken)
	log.write("====================\n\n")
	
	#Select appropriate plan file handler
	planFileHandler = PLAN_FILE_HANDLERS[job.plannerName]
	planFileHandler(log, job.planFile)
		
	#Validate the plan
	log.write("Plan Validation\n")
	log.flush()
	call_args = "%s"%(job.validatorCommand)
	subprocess.call(call_args, shell=True, stdout=log, stderr=log)
	
	log.write("===EOF===")
	log.close()

	#Compress files to save space
	with open(job.logFile, 'rb') as f_in, gzip.open(job.logFile + '.gz', 'wb') as f_out:
		shutil.copyfileobj(f_in, f_out)
		f_in.close()
		f_out.close()
	#Remove uncompressed files
	os.remove(job.logFile)

	#Check for plan file before compressing
	planFilePath = Path(job.planFile)
	#printMessage("Checking for file %s"%planFilePath)
	if planFilePath.is_file(): 
		with open(job.planFile, 'rb') as f_in, gzip.open(job.planFile + '.gz', 'wb') as f_out:
				shutil.copyfileobj(f_in, f_out)
				f_in.close()
				f_out.close()
		#Remove uncompressed files
		os.remove(job.planFile)	

def shutdownSocket(aSocket):
	try:
		aSocket.shutdown(socket.SHUT_RDWR)
		aSocket.close()
	except OSError as e:
		print ("Error shutting down socket: %s"%str(e))
	time.sleep(1)

def main(args):

	parser = argparse.ArgumentParser(description='A worker daemon for completing experiments obtained from a server.')
	parser.add_argument('server',
						metavar='127.0.0.1',
						nargs="?",
						default=DEFAULT_IP,
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
	try:
		server = str(ipaddress.ip_address(server))
	except Exception as e:
		print('Error: %s.' %(str(e)))
		sys.exit(1)

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
		clientsocket.connect((server, port))
		hostname = socket.gethostname()
		msg = getMessageString(_id, REQUEST_PROBLEM, hostname)
		clientsocket.sendall(msg)

		data = clientsocket.recv(BUFFER_SIZE)
		reply = getMessage(data)

		#Check if the buffer is empty
		if reply.message == EXIT_PROCESS:
			msg = getMessageString(_id, "Ack. Exiting...", hostname)
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
