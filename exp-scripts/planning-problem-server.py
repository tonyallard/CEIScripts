#!/usr/bin/python
import sys
import os
import socket
import pickle
from cStringIO import StringIO
from multiprocessing import Queue
import time

from PlanningProblemConstants import *
from PlanningProblemJob import *

#Socket Parameters
HOST = socket.gethostname()
PORT = 50005
BUFFER_SIZE = 4096
QUEUED_CONNECTIONS = 10 #Have set this to the number of workers

#Planner Parameters
PLANNER_LOC="/mnt/data/bin/Colin2-withStatePrinter/"
PLANNER_EXEC_LOC="/mnt/data/bin/Colin2-withStatePrinter/debug/colin/colin-clp"
PLANNER_PARAMS = "-h -v1"
TIMEOUT_CMD="timeout -s SIGXCPU 30m" #30mins
TIME_CMD = "time -p"
MEMLIMIT_CMD="ulimit -Sv 2000000" #2GB

#Validation Parameters
VALIDATOR_EXEC = "/mnt/data/bin/VAL/validate"
VALIDATOR_PARAMS = "-t 0.001 -v"

#File Locations
LOG_FOLDER="/mnt/data/logs/"
PROBLEM_SETS="/mnt/data/problem-sets/"
PLANS_FOLDER = "plans"
OUTPUT_FOLDER = "output"
#Constants
DOMAIN_FILE = "DOMAIN.PDDL"
IGNORE_SET_LIST = ["archive"]

def setupFolderStructure(plansdir_fullpath, outputdir_fullpath):
	if not os.path.exists(plansdir_fullpath):
		os.makedirs(plansdir_fullpath)
	if not os.path.exists(outputdir_fullpath):
		os.makedirs(outputdir_fullpath)

def getProblemFiles(path):
	problems = []
	for root, dirs, files in os.walk(path):
		for file in files:
			if file != DOMAIN_FILE:
				problems.append(file)
	return problems


def getProblemQueue(iterations=2):
	#The Queue
	q = Queue()
	#iterate through problem sets
	for root, dirs, files in os.walk(PROBLEM_SETS):
		for subdir in dirs:
			if subdir in IGNORE_SET_LIST:
				continue
			#Get full problem path
			subdir_fullpath = os.path.join(root, subdir)
			domainFile = os.path.join(subdir_fullpath, DOMAIN_FILE)
			#Ger full path for plan and logs
			plansdir_fullpath = os.path.join(LOG_FOLDER, subdir, PLANS_FOLDER)
			outputdir_fullpath = os.path.join(LOG_FOLDER, subdir, OUTPUT_FOLDER)
			#Create missing folders, if any
			setupFolderStructure(plansdir_fullpath, outputdir_fullpath)
			
			problems = getProblemFiles(subdir_fullpath)
			
			for prob in problems:
				#Problem file
				probFile = os.path.join(subdir_fullpath, prob)
				#Planner command
				plannener_command = "(cd %s && %s && %s %s %s %s %s %s)"%(PLANNER_LOC, 
					MEMLIMIT_CMD, TIME_CMD, TIMEOUT_CMD, PLANNER_EXEC_LOC, 
					PLANNER_PARAMS, domainFile, probFile)

				for itr in range(0, iterations):
					#Plan file
					planFileName = "%s-%i.plan"%(prob, itr)
					planFile = os.path.join(plansdir_fullpath, planFileName)
					#Validate command
					validate_command = "(%s %s %s %s %s)" % (VALIDATOR_EXEC, 
						VALIDATOR_PARAMS, domainFile, probFile, planFile)
					#Log file
					logFileName = "%s-%i.txt"%(prob, itr)
					commandList = [plannener_command, validate_command]
					logFile = os.path.join(outputdir_fullpath, logFileName)
					job = Job(prob, itr, plannener_command, 
						validate_command, logFile, planFile)
					q.put(job)				
		#The first entry has all the dirs
		break
	return q

def main(args):

	#Get problems ready for computation
	q = getProblemQueue()

	#create an INET, STREAMing socket
	serversocket = socket.socket(
    	socket.AF_INET, socket.SOCK_STREAM)
	serversocket.setsockopt(socket.SOL_SOCKET, 
		socket.SO_REUSEADDR, 1)
	#bind the socket to a public host,
	# and a well-known port
	serversocket.bind((HOST, PORT))

	#Listen for workers and give them work
	serversocket.listen(QUEUED_CONNECTIONS)
	while True:
		#become a server socket
		conn, addr = serversocket.accept()
		data = conn.recv(BUFFER_SIZE)
		print data
		if data == EXIT_PROCESS:
			conn.sendall("Ack. Exiting...")
			conn.shutdown(socket.SHUT_RDWR)
			conn.close()
			time.sleep(1)
			sys.exit(0)
		elif data == PROBLEM_QUEUE_SIZE:
			conn.sendall("Ack. Queue size is %i"%q.qsize())
		elif data == REQUEST_PROBLEM:
			if q.empty(): #Tell the workers to terminate if done
				print "Received request from %s, but queue is empty. \
				Instructing worker to terminate."%addr
				conn.sendall(EXIT_PROCESS)
			else: #Else give it a job
				job = q.get()
				print "Processing %s for iteration %i on %s" %(job.problemName, 
					job.itr, str(addr))
				stream = StringIO() 
				pickle.dump(job, stream)
				conn.sendall(stream.getvalue())
				stream.close()
		#Close and get ready for next conn
		conn.close()

#Run Main Function
if __name__ == "__main__":
	main(sys.argv)