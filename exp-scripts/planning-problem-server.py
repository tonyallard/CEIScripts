#!/usr/bin/python
import sys
import os
import socket
from multiprocessing import Queue
import time
import re
import time
import datetime

from PlanningProblemConstants import *
from PlanningProblemJob import *

#Socket Parameters
HOST = "" #Don't restrict listener to any machine
PORT = 50005
BUFFER_SIZE = 8192
QUEUED_CONNECTIONS = 50 #Have set this to the number of workers

#Function to make command like most colin planners
COLIN_PLANNER_PARAMS = "-v1"
def getColinStylePlannerCommand(plannerDir, plannerExecLocation, 
	domainFile, probFile, freeParams=COLIN_PLANNER_PARAMS):
	return "(cd %s && %s && %s %s %s %s %s %s)"%(plannerDir,
		MEMLIMIT_CMD, TIME_CMD, TIMEOUT_CMD, plannerExecLocation,
		freeParams, domainFile, probFile)

#Planner Parameters
#Colin-TRH
def colinTRHcolin(domainFile, probFile, planFile=""):
	PLANNER_LOC="/mnt/data/bin/Colin2-trh-colin/"
	PLANNER_EXEC_LOC="/mnt/data/bin/Colin2-trh-colin/release/colin/colin-clp"
	return getColinStylePlannerCommand(PLANNER_LOC, 
		PLANNER_EXEC_LOC, domainFile, probFile)

#Colin-TRH-Ablation
def colinTRHcolinAblation(domainFile, probFile, planFile=""):
	PLANNER_LOC="/mnt/data/bin/colin-trh-ablation/"
	PLANNER_EXEC_LOC="/mnt/data/bin/colin-trh-ablation/release/colin/colin-clp"
	return getColinStylePlannerCommand(PLANNER_LOC, 
		PLANNER_EXEC_LOC, domainFile, probFile)

#Popf-TRH
def popfTRHpopf(domainFile, probFile, planFile=""):
	PLANNER_LOC="/mnt/data/bin/popf-trh-popf/"
	PLANNER_EXEC_LOC="/mnt/data/bin/popf-trh-popf/compile/popf2/popf3-clp"
	return getColinStylePlannerCommand(PLANNER_LOC, 
		PLANNER_EXEC_LOC, domainFile, probFile)

#Popf-TRH-Ablation
def popfTRHpopfAblation(domainFile, probFile, planFile=""):
	PLANNER_LOC="/mnt/data/bin/popf-trh-ablation/"
	PLANNER_EXEC_LOC="/mnt/data/bin/popf-trh-ablation/compile/popf2/popf3-clp"
	return getColinStylePlannerCommand(PLANNER_LOC, 
		PLANNER_EXEC_LOC, domainFile, probFile)

#Colin-TRH No Steepest Descent
def colinTRHcolinNoSD(domainFile, probFile, planFile=""):
	PLANNER_LOC="/mnt/data/bin/Colin2-trh-colin/"
	PLANNER_EXEC_LOC="/mnt/data/bin/Colin2-trh-colin/release/colin/colin-clp"
	PLANNER_PARAMS = "-e " + COLIN_PLANNER_PARAMS
	return getColinStylePlannerCommand(PLANNER_LOC, 
		PLANNER_EXEC_LOC, domainFile, probFile, PLANNER_PARAMS)

#Colin-TRH-Ablation No Steepest Descent
def colinTRHcolinAblationNoSD(domainFile, probFile, planFile=""):
	PLANNER_LOC="/mnt/data/bin/colin-trh-ablation/"
	PLANNER_EXEC_LOC="/mnt/data/bin/colin-trh-ablation/release/colin/colin-clp"
	PLANNER_PARAMS = "-e " + COLIN_PLANNER_PARAMS
	return getColinStylePlannerCommand(PLANNER_LOC, 
		PLANNER_EXEC_LOC, domainFile, probFile, PLANNER_PARAMS)

#Popf-TRH No Steepest Descent
def popfTRHpopfNoSD(domainFile, probFile, planFile=""):
	PLANNER_LOC="/mnt/data/bin/popf-trh-popf/"
	PLANNER_EXEC_LOC="/mnt/data/bin/popf-trh-popf/compile/popf2/popf3-clp"
	PLANNER_PARAMS = "-e " + COLIN_PLANNER_PARAMS
	return getColinStylePlannerCommand(PLANNER_LOC, 
		PLANNER_EXEC_LOC, domainFile, probFile, PLANNER_PARAMS)

#Popf-TRH-Ablation No Steepest Descent
def popfTRHpopfAblationNoSD(domainFile, probFile, planFile=""):
	PLANNER_LOC="/mnt/data/bin/popf-trh-ablation/"
	PLANNER_EXEC_LOC="/mnt/data/bin/popf-trh-ablation/compile/popf2/popf3-clp"
	PLANNER_PARAMS = "-e " + COLIN_PLANNER_PARAMS
	return getColinStylePlannerCommand(PLANNER_LOC, 
		PLANNER_EXEC_LOC, domainFile, probFile, PLANNER_PARAMS)

#Colin-RPG
def colinRPG(domainFile, probFile, planFile=""):
	PLANNER_LOC="/mnt/data/bin/colin2/"
	PLANNER_EXEC_LOC="/mnt/data/bin/colin2/release/colin/colin-clp"
	return getColinStylePlannerCommand(PLANNER_LOC, 
		PLANNER_EXEC_LOC, domainFile, probFile)

#Colin-RPG No Steepest Descent
def colinRPGNoSD(domainFile, probFile, planFile=""):
	PLANNER_LOC="/mnt/data/bin/colin2/"
	PLANNER_EXEC_LOC="/mnt/data/bin/colin2/release/colin/colin-clp"
	PLANNER_PARAMS = "-e " + COLIN_PLANNER_PARAMS
	return getColinStylePlannerCommand(PLANNER_LOC, 
		PLANNER_EXEC_LOC, domainFile, probFile, PLANNER_PARAMS)

#POPF
def popf(domainFile, probFile, planFile=""):
	PLANNER_LOC="/mnt/data/bin/tempo-sat-popf2/"
	PLANNER_EXEC_LOC="/mnt/data/bin/tempo-sat-popf2/compile/popf2/popf3-clp"
	return getColinStylePlannerCommand(PLANNER_LOC, 
		PLANNER_EXEC_LOC, domainFile, probFile)

#POPF No Steepest Descent
def popfNoSD(domainFile, probFile, planFile=""):
	PLANNER_LOC="/mnt/data/bin/tempo-sat-popf2/"
	PLANNER_EXEC_LOC="/mnt/data/bin/tempo-sat-popf2/compile/popf2/popf3-clp"
	PLANNER_PARAMS = "-e " + COLIN_PLANNER_PARAMS
	return getColinStylePlannerCommand(PLANNER_LOC, 
		PLANNER_EXEC_LOC, domainFile, probFile, PLANNER_PARAMS)

#OPTIC
def optic(domainFile, probFile, planFile=""):
	PLANNER_LOC="/mnt/data/bin/optic/"
	PLANNER_EXEC_LOC="/mnt/data/bin/optic/release/optic/optic-clp"
	PLANNER_PARAMS = "-N " + COLIN_PLANNER_PARAMS
	return getColinStylePlannerCommand(PLANNER_LOC, 
		PLANNER_EXEC_LOC, domainFile, probFile, PLANNER_PARAMS)

#OPTIC - TIL Relaxation Turned off
def opticSLFRP(domainFile, probFile, planFile=""):
	PLANNER_LOC="/mnt/data/bin/optic/"
	PLANNER_EXEC_LOC="/mnt/data/bin/optic/release/optic/optic-clp"
	PLANNER_PARAMS = "-N -0 " + COLIN_PLANNER_PARAMS
	return getColinStylePlannerCommand(PLANNER_LOC, 
		PLANNER_EXEC_LOC, domainFile, probFile, PLANNER_PARAMS)

def lpgtd(domainFile, probFile, planFile):
	PLANNER_LOC="/mnt/data/bin/lpg-td/"
	PLANNER_EXEC_LOC="/mnt/data/bin/lpg-td/lpg-td-1.0.1"
	PLANNER_PARAMS = "-n 1"

	return "(cd %s && %s && %s %s %s -o %s -f %s -out %s %s)"%(PLANNER_LOC,
		MEMLIMIT_CMD, TIME_CMD, TIMEOUT_CMD, PLANNER_EXEC_LOC,
		domainFile, probFile, planFile, PLANNER_PARAMS)
		
#tplan
def tplan(domainFile, probFile, planFile=""):
	PLANNER_LOC="/exp/planners/tplan/"
	PLANNER_EXEC_LOC="/exp/planners/tplan/compile/planner/tplan"
	PLANNER_PARAMS = ""
	
	return "(cd %s && %s && %s %s %s %s %s %s)"%(PLANNER_LOC,
		MEMLIMIT_CMD, TIME_CMD, TIMEOUT_CMD, PLANNER_EXEC_LOC,
		domainFile, probFile, PLANNER_PARAMS)

#Limit Commands
TIMEOUT_CMD="timeout -s SIGXCPU 30m" #30mins
TIME_CMD = "time -p"
MEMLIMIT_CMD="ulimit -Sv 4000000" #4GB

#Validation Parameters
VALIDATOR_EXEC = "/mnt/exp/VAL/validate"
VALIDATOR_PARAMS = "-t 0.001 -v"

#File Locations
LOG_FOLDER="/mnt/exp/logs/"
PROBLEM_SETS="/mnt/exp/problems/"
PLANS_FOLDER = "plans"
OUTPUT_FOLDER = "output"
#Constants
DOMAIN_FILE = "DOMAIN.PDDL"
IGNORE_SET_LIST = ["archive", "archive2", "archive3"]
AIRPORT_PROBLEM = ["airport", "airport-tighten"]

PROBLEM_FILE_SYNTAX = "\(define *\t*\(problem *\t*[a-zA-Z0-9_\-]*\)"
PROBLEM_FILE_REGEX = re.compile(PROBLEM_FILE_SYNTAX)

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
				filePTR = open(os.path.join(path, file), 'r')
				filetext = filePTR.read()
				filePTR.close()
				matches = PROBLEM_FILE_REGEX.findall(filetext)
				if len(matches) > 0:
					problems.append(file)
	return problems

def getProblemQueue(iterations=1, start=0):
	#The Queue
	q = Queue()
	planners = {
		#"Colin-RPG" : colinRPG,
		#"NoSD-Colin-RPG" : colinRPGNoSD,
		#"POPF-RPG" : popf,
		#"NoSD-POPF-RPG" : popfNoSD,
		#"Optic-RPG" : optic,
		#"Optic-SLFRP" : opticSLFRP,
		#"lpg-td" : lpgtd,
		#"Colin-TRH-Colin" : colinTRHcolin,
		#"ablation-Colin-TRH-Colin": colinTRHcolinAblation,
		#"Popf-TRH-Popf" : popfTRHpopf,
		#"ablation-Popf-TRH-Popf" : popfTRHpopfAblation,
		#"NoSD-Colin-TRH-Colin" : colinTRHcolinNoSD,
		#"NoSD-ablation-Colin-TRH-Colin": colinTRHcolinAblationNoSD,
		#"NoSD-Popf-TRH-Popf" : popfTRHpopfNoSD,
		#"NoSD-ablation-Popf-TRH-Popf" : popfTRHpopfAblationNoSD
		"tplan" : tplan
	}
	#iterate through planners
	for planner in planners:
		#Get function to create planner command
		f = planners[planner]
		#iterate through problem sets
		for root, dirs, files in os.walk(PROBLEM_SETS):
			for subdir in dirs:
				if subdir in IGNORE_SET_LIST:
					continue
				#Get full problem path
				subdir_fullpath = os.path.join(root, subdir)
				#Ger full path for plan and logs
				plansdir_fullpath = os.path.join(LOG_FOLDER, planner, subdir, PLANS_FOLDER)
				outputdir_fullpath = os.path.join(LOG_FOLDER, planner, subdir, OUTPUT_FOLDER)
				#Create missing folders, if any
				setupFolderStructure(plansdir_fullpath, outputdir_fullpath)
				
				problems = getProblemFiles(subdir_fullpath)
				
				for prob in problems:
					#Problem file
					probFile = os.path.join(subdir_fullpath, prob)
					#Domain file
					domainFile = os.path.join(subdir_fullpath, DOMAIN_FILE)
					#Special case for the Airport domain
					#As this has a domain file for each problem file
					if subdir in AIRPORT_PROBLEM:
						domainFile = os.path.join(subdir_fullpath,  prob[0:4] + DOMAIN_FILE)

					for itr in range(start, start+iterations):
						#Plan file
						planFileName = "%s-%i.plan"%(prob, itr)						
						planFile = os.path.join(plansdir_fullpath, planFileName)

						#Planner command
						planner_command = f(domainFile, probFile, planFile)

						#Validate command
						validate_command = "(%s %s %s %s %s)" % (VALIDATOR_EXEC, 
							VALIDATOR_PARAMS, domainFile, probFile, planFile)
						#Log file
						logFileName = "%s-%i.txt"%(prob, itr)
						logFile = os.path.join(outputdir_fullpath, logFileName)
						#Generate job
						job = Job(planner, prob, itr, planner_command, 
							validate_command, logFile, planFile)
						q.put(job)
			#The first entry has all the dirs
			break
	return q

def getCurrentAllocationString(currentAllocation):
	result = ""
	for _id in currentAllocation:
		duration = time.time() - currentAllocation[_id][4]
		result += "%s [%s] (%i): %s (%i) [%s]\n"%(currentAllocation[_id][1],
			currentAllocation[_id][0], _id, 
			currentAllocation[_id][2], currentAllocation[_id][3], 
			str(datetime.timedelta(seconds=duration)))

	return result

def getNumberOfWorkersExecuting(currentAllocation):
	numExecutions = 0
	for _id in currentAllocation:
		if currentAllocation[_id][2] not in [WORKER_PAUSED, WORKER_TERMINATED]:
			numExecutions += 1
	return numExecutions

def shutdownSocket(aSocket):
	aSocket.shutdown(socket.SHUT_RDWR)
	aSocket.close()
	time.sleep(1)

def main(args):

	_id = getInstanceID()
	printMessage("Started. My ID is %i"%_id)

	#Get problems ready for computation
	q = getProblemQueue()
	printMessage("Problem queue initialised with %i problems."%q.qsize())
	#Current allocation data structure
	#Indexed by id, then list. Elements:
	#0: IP
	#1: Hostname
	#2: STATUS
	#3: Problem Name (iteration)
	#4: Timestamp of last command
	currentAllocation = {}

	#create an INET, STREAMing socket
	serversocket = socket.socket(
    	socket.AF_INET, socket.SOCK_STREAM)
	serversocket.setsockopt(socket.SOL_SOCKET, 
		socket.SO_REUSEADDR, 1)
	#bind the socket to a public host,
	# and a well-known port
	serversocket.bind((HOST, PORT))
	paused = False
	terminate = False
	restrictWorkers = True
	#Listen for workers and give them work
	serversocket.listen(QUEUED_CONNECTIONS)
	while True:
		#become a server socket
		conn, addr = serversocket.accept()
		data = conn.recv(BUFFER_SIZE)
		message = getMessage(data)

		reply = ""
		if message.message == EXIT_PROCESS:
			printMessage("Exit cmd recieved from machine %s with id %i" %(addr, 
				message._id))
			reply = getMessageString(_id, "Ack. Exiting...")
			conn.sendall(reply)
			conn.shutdown(socket.SHUT_RDWR)
			conn.close()
			shutdownSocket(serversocket)
			break
		elif message.message == PROBLEM_QUEUE_SIZE:
			printMessage("Queue size request recieved from machine %s with id %i"%(addr, 
				message._id))
			reply = getMessageString(_id, "Ack. Queue size is %i"%q.qsize())
		elif message.message == REQUEST_PROBLEM:
			#Pause the worker because it is done.
			currentAllocation[message._id] = (addr[0], message.hostname, WORKER_PAUSED, 0, 
				time.time())
			
			if q.empty(): #Tell the workers to terminate if done
				printMessage("Received request from machine %s with id %i, but queue is empty. Instructing worker to terminate."%(addr, 
							message._id))
				reply = getMessageString(_id, EXIT_PROCESS)
				currentAllocation[message._id] = (addr[0], message.hostname, WORKER_TERMINATED, 0,
					time.time())
			elif terminate:
				printMessage("Received request from machine %s with id %i, but have been instructed to terminate workers. Instructing worker to terminate."%(addr, 
							message._id))
				reply = getMessageString(_id, EXIT_PROCESS)
				currentAllocation[message._id] = (addr[0], message.hostname, WORKER_TERMINATED, 0,
					time.time())
			elif paused:
				printMessage("Received request from machine %s with id %i, but computation is currently Paused. Instructing worker to wait."%(addr, 
							message._id))
				reply = getMessageString(_id, WORKER_PAUSED)
			elif (restrictWorkers and getNumberOfWorkersExecuting(currentAllocation) >= RESTRICTED_WORKER_NUMBER):
				printMessage("Received request from machine %s with id %i, but computation is being restricted and is currently at limit. Instructing worker to wait."%(addr, 
					message._id))
				reply = getMessageString(_id, WORKER_PAUSED)
			else: #Else give it a job
				job = q.get()
				printMessage("Processing %s for iteration %i on machine %s with id %i"%(job.problemName, 
					job.itr, addr, message._id))
				reply = getMessageString(_id, job)
				currentAllocation[message._id] = (addr[0], message.hostname, job.problemName, job.itr,
					time.time())
		elif message.message == CURRENT_ALLOCATION:
			printMessage("Received request from machine %s with id %i for current allocation."%(addr, 
				message._id))
			reply = getMessageString(_id, 
				getCurrentAllocationString(currentAllocation))
		elif message.message == PAUSE_WORKERS:
			paused = True
			printMessage("Pause cmd recieved from machine %s with id %i" %(addr, 
				message._id))
			reply = getMessageString(_id, "Ack. Pausing...")
		elif message.message == TERMINATE_WORKERS:
			terminate = True
			printMessage("Terminate cmd recieved from machine %s with id %i" %(addr, 
				message._id))
			reply = getMessageString(_id, "Ack. Terminating...")
		elif message.message == RESUME_WORKERS:
			paused = False
			printMessage("Resume cmd recieved from machine %s with id %i" %(addr, 
				message._id))
			reply = getMessageString(_id, "Ack. Resuming...")
		elif message.message == RESTRICT_WORKERS:
			restrictWorkers = True
			printMessage("Restrict workers cmd recieved from machine %s with id %i" %(addr, 
				message._id))
			reply = getMessageString(_id, "Ack. Restricting workers...")
		elif message.message == UNRESTRICT_WORKERS:
			restrictWorkers = False
			printMessage("Relax worker restriction cmd recieved from machine %s with id %i" %(addr, 
				message._id))
			reply = getMessageString(_id, "Ack. Setting workers free...")

		#Send the reply
		conn.sendall(reply)
		#Close and get ready for next conn
		conn.close()

#Run Main Function
if __name__ == "__main__":
	main(sys.argv)
