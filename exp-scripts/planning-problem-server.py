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

DEFAULT_ROOT_DIR = "/exp"

#Function to make command like most colin planners
COLIN_PLANNER_PARAMS = "-v1"
def getColinStylePlannerCommand(plannerDir, plannerExecLocation, 
	domainFile, probFile, freeParams=COLIN_PLANNER_PARAMS):
	return "(cd %s && %s && %s %s %s %s %s %s)"%(plannerDir,
		MEMLIMIT_CMD, TIME_CMD, TIMEOUT_CMD, plannerExecLocation,
		freeParams, domainFile, probFile)

#Planner Parameters
#Colin-TRH
def colinTRHcolin(domainFile, probFile, planFile="", confFile=""):
	PLANNER_LOC= os.path.join(DEFAULT_ROOT_DIR, "planners/Colin2-trh-colin/")
	PLANNER_EXEC_LOC= os.path.join(DEFAULT_ROOT_DIR, "planners/Colin2-trh-colin/release/colin/colin-clp")
	return getColinStylePlannerCommand(PLANNER_LOC, 
		PLANNER_EXEC_LOC, domainFile, probFile)

#Colin-TRH-Ablation
def colinTRHcolinAblation(domainFile, probFile, planFile="", confFile=""):
	PLANNER_LOC= os.path.join(DEFAULT_ROOT_DIR, "planners/colin-trh-ablation/")
	PLANNER_EXEC_LOC= os.path.join(DEFAULT_ROOT_DIR, "planners/colin-trh-ablation/release/colin/colin-clp")
	return getColinStylePlannerCommand(PLANNER_LOC, 
		PLANNER_EXEC_LOC, domainFile, probFile)

#Popf-TRH
def popfTRHpopf(domainFile, probFile, planFile="", confFile=""):
	PLANNER_LOC= os.path.join(DEFAULT_ROOT_DIR, "planners/popf-trh-popf/")
	PLANNER_EXEC_LOC= os.path.join(DEFAULT_ROOT_DIR, "planners/popf-trh-popf/compile/popf2/popf3-clp")
	return getColinStylePlannerCommand(PLANNER_LOC, 
		PLANNER_EXEC_LOC, domainFile, probFile)

#Popf-TRH-Ablation
def popfTRHpopfAblation(domainFile, probFile, planFile="", confFile=""):
	PLANNER_LOC= os.path.join(DEFAULT_ROOT_DIR, "planners/popf-trh-ablation/")
	PLANNER_EXEC_LOC= os.path.join(DEFAULT_ROOT_DIR, "planners/popf-trh-ablation/compile/popf2/popf3-clp")
	return getColinStylePlannerCommand(PLANNER_LOC, 
		PLANNER_EXEC_LOC, domainFile, probFile)

#Colin-TRH No Steepest Descent
def colinTRHcolinNoSD(domainFile, probFile, planFile="", confFile=""):
	PLANNER_LOC= os.path.join(DEFAULT_ROOT_DIR, "planners/Colin2-trh-colin/")
	PLANNER_EXEC_LOC= os.path.join(DEFAULT_ROOT_DIR, "planners/Colin2-trh-colin/release/colin/colin-clp")
	PLANNER_PARAMS = "-e " + COLIN_PLANNER_PARAMS
	return getColinStylePlannerCommand(PLANNER_LOC, 
		PLANNER_EXEC_LOC, domainFile, probFile, PLANNER_PARAMS)

#Colin-TRH-Ablation No Steepest Descent
def colinTRHcolinAblationNoSD(domainFile, probFile, planFile="", confFile=""):
	PLANNER_LOC= os.path.join(DEFAULT_ROOT_DIR, "planners/colin-trh-ablation/")
	PLANNER_EXEC_LOC= os.path.join(DEFAULT_ROOT_DIR, "planners/colin-trh-ablation/release/colin/colin-clp")
	PLANNER_PARAMS = "-e " + COLIN_PLANNER_PARAMS
	return getColinStylePlannerCommand(PLANNER_LOC, 
		PLANNER_EXEC_LOC, domainFile, probFile, PLANNER_PARAMS)

#Popf-TRH No Steepest Descent
def popfTRHpopfNoSD(domainFile, probFile, planFile="", confFile=""):
	PLANNER_LOC= os.path.join(DEFAULT_ROOT_DIR, "planners/popf-trh-popf/")
	PLANNER_EXEC_LOC= os.path.join(DEFAULT_ROOT_DIR, "planners/popf-trh-popf/compile/popf2/popf3-clp")
	PLANNER_PARAMS = "-e " + COLIN_PLANNER_PARAMS
	return getColinStylePlannerCommand(PLANNER_LOC, 
		PLANNER_EXEC_LOC, domainFile, probFile, PLANNER_PARAMS)

#Popf-TRH-Ablation No Steepest Descent
def popfTRHpopfAblationNoSD(domainFile, probFile, planFile="", confFile=""):
	PLANNER_LOC= os.path.join(DEFAULT_ROOT_DIR, "planners/popf-trh-ablation/")
	PLANNER_EXEC_LOC= os.path.join(DEFAULT_ROOT_DIR, "planners/popf-trh-ablation/compile/popf2/popf3-clp")
	PLANNER_PARAMS = "-e " + COLIN_PLANNER_PARAMS
	return getColinStylePlannerCommand(PLANNER_LOC, 
		PLANNER_EXEC_LOC, domainFile, probFile, PLANNER_PARAMS)

#Colin-RPG
def colinRPG(domainFile, probFile, planFile="", confFile=""):
	PLANNER_LOC= os.path.join(DEFAULT_ROOT_DIR, "planners/colin2/")
	PLANNER_EXEC_LOC= os.path.join(DEFAULT_ROOT_DIR, "planners/colin2/release/colin/colin-clp")
	return getColinStylePlannerCommand(PLANNER_LOC, 
		PLANNER_EXEC_LOC, domainFile, probFile)

#Colin-RPG No Steepest Descent
def colinRPGNoSD(domainFile, probFile, planFile="", confFile=""):
	PLANNER_LOC= os.path.join(DEFAULT_ROOT_DIR, "planners/colin2/")
	PLANNER_EXEC_LOC= os.path.join(DEFAULT_ROOT_DIR, "planners/colin2/release/colin/colin-clp")
	PLANNER_PARAMS = "-e " + COLIN_PLANNER_PARAMS
	return getColinStylePlannerCommand(PLANNER_LOC, 
		PLANNER_EXEC_LOC, domainFile, probFile, PLANNER_PARAMS)

#POPF
def popf(domainFile, probFile, planFile="", confFile=""):
	PLANNER_LOC= os.path.join(DEFAULT_ROOT_DIR, "planners/tempo-sat-popf2/")
	PLANNER_EXEC_LOC= os.path.join(DEFAULT_ROOT_DIR, "planners/tempo-sat-popf2/compile/popf2/popf3-clp")
	return getColinStylePlannerCommand(PLANNER_LOC, 
		PLANNER_EXEC_LOC, domainFile, probFile)

#POPF No Steepest Descent
def popfNoSD(domainFile, probFile, planFile="", confFile=""):
	PLANNER_LOC= os.path.join(DEFAULT_ROOT_DIR, "planners/tempo-sat-popf2/")
	PLANNER_EXEC_LOC= os.path.join(DEFAULT_ROOT_DIR, "planners/tempo-sat-popf2/compile/popf2/popf3-clp")
	PLANNER_PARAMS = "-e " + COLIN_PLANNER_PARAMS
	return getColinStylePlannerCommand(PLANNER_LOC, 
		PLANNER_EXEC_LOC, domainFile, probFile, PLANNER_PARAMS)

#OPTIC
def optic(domainFile, probFile, planFile="", confFile=""):
	PLANNER_LOC= os.path.join(DEFAULT_ROOT_DIR, "planners/optic/")
	PLANNER_EXEC_LOC= os.path.join(DEFAULT_ROOT_DIR, "planners/optic/release/optic/optic-clp")
	PLANNER_PARAMS = "-N " + COLIN_PLANNER_PARAMS
	return getColinStylePlannerCommand(PLANNER_LOC, 
		PLANNER_EXEC_LOC, domainFile, probFile, PLANNER_PARAMS)

#OPTIC - TIL Relaxation Turned off
def opticSLFRP(domainFile, probFile, planFile="", confFile=""):
	PLANNER_LOC= os.path.join(DEFAULT_ROOT_DIR, "planners/optic/")
	PLANNER_EXEC_LOC= os.path.join(DEFAULT_ROOT_DIR, "planners/optic/release/optic/optic-clp")
	PLANNER_PARAMS = "-N -0 " + COLIN_PLANNER_PARAMS
	return getColinStylePlannerCommand(PLANNER_LOC, 
		PLANNER_EXEC_LOC, domainFile, probFile, PLANNER_PARAMS)

def lpgtd(domainFile, probFile, planFile, confFile=""):
	PLANNER_LOC= os.path.join(DEFAULT_ROOT_DIR, "planners/lpg-td/")
	PLANNER_EXEC_LOC= os.path.join(DEFAULT_ROOT_DIR, "planners/lpg-td/lpg-td-1.0.1")
	PLANNER_PARAMS = "-n 1"

	return "(cd %s && %s && %s %s %s -o %s -f %s -out %s %s)"%(PLANNER_LOC,
		MEMLIMIT_CMD, TIME_CMD, TIMEOUT_CMD, PLANNER_EXEC_LOC,
		domainFile, probFile, planFile, PLANNER_PARAMS)
		
#tplan
def tplanS0T0(domainFile, probFile, planFile="", confFile=""):
	return base_tplan(0, 0, domainFile, probFile, planFile, confFile)
		
def tplanS0T1(domainFile, probFile, planFile="", confFile=""):
	return base_tplan(0, 1, domainFile, probFile, planFile, confFile)
		
def tplanS1T0(domainFile, probFile, planFile="", confFile=""):
	return base_tplan(1, 0, domainFile, probFile, planFile, confFile)
		
def tplanS1T1(domainFile, probFile, planFile="", confFile=""):
	return base_tplan(1, 1, domainFile, probFile, planFile, confFile)
			
def tplanS2T0(domainFile, probFile, planFile="", confFile=""):
	return base_tplan(2, 0, domainFile, probFile, planFile, confFile)
	
def tplanS2T1(domainFile, probFile, planFile="", confFile=""):
	return base_tplan(2, 1, domainFile, probFile, planFile, confFile)
	
def tplanS3T0(domainFile, probFile, planFile="", confFile=""):
	return base_tplan(3, 0, domainFile, probFile, planFile, confFile)
	
def tplanS3T1(domainFile, probFile, planFile="", confFile=""):
	return base_tplan(3, 1, domainFile, probFile, planFile, confFile)
	
def tplanS4T0(domainFile, probFile, planFile="", confFile=""):
	return base_tplan(4, 0, domainFile, probFile, planFile, confFile)
	
def tplanS4T1(domainFile, probFile, planFile="", confFile=""):
	return base_tplan(4, 1, domainFile, probFile, planFile, confFile)
	
def tplanS5T0(domainFile, probFile, planFile="", confFile=""):
	return base_tplan(5, 0, domainFile, probFile, planFile, confFile)
	
def tplanS5T1(domainFile, probFile, planFile="", confFile=""):
	return base_tplan(5, 1, domainFile, probFile, planFile, confFile)
	
def tplanS6T0(domainFile, probFile, planFile="", confFile=""):
	return base_tplan(6, 0, domainFile, probFile, planFile, confFile)
	
def tplanS6T1(domainFile, probFile, planFile="", confFile=""):
	return base_tplan(6, 1, domainFile, probFile, planFile, confFile)
	
def tplanS7T0(domainFile, probFile, planFile="", confFile=""):
	return base_tplan(7, 0, domainFile, probFile, planFile, confFile)
	
def tplanS7T1(domainFile, probFile, planFile="", confFile=""):
	return base_tplan(7, 1, domainFile, probFile, planFile, confFile)
		
def base_tplan(strategy, application, domainFile, probFile, planFile="", confFile=""):
	PLANNER_LOC= os.path.join(DEFAULT_ROOT_DIR, "planners/tplan/")
	PLANNER_EXEC_LOC= os.path.join(DEFAULT_ROOT_DIR, "planners/tplan/compile/planner/tplan")
	PLANNER_PARAMS = "-v 5 -s %i -t %i"%(strategy, application)
	if len(confFile) > 0:
		PLANNER_PARAMS = PLANNER_PARAMS + " -c"
	
	return "(cd %s && %s && %s %s %s %s %s %s %s)"%(PLANNER_LOC,
		MEMLIMIT_CMD, TIME_CMD, TIMEOUT_CMD, PLANNER_EXEC_LOC,
		domainFile, probFile, PLANNER_PARAMS, confFile)
			
def metricff(domainFile, probFile, planFile=""):
	PLANNER_LOC= os.path.join(DEFAULT_ROOT_DIR, "planners/Metric-FF-v2.1")
	PLANNER_EXEC_LOC= os.path.join(DEFAULT_ROOT_DIR, "planners/Metric-FF-v2.1/ff")
	PLANNER_PARAMS = "-s 0"

	return "(cd %s && %s && %s %s %s -o %s -f %s %s)"%(PLANNER_LOC,
		MEMLIMIT_CMD, TIME_CMD, TIMEOUT_CMD, PLANNER_EXEC_LOC,
		domainFile, probFile, PLANNER_PARAMS)
		
def cpt_yahsp(domainFile, probFile, planFile=""):
	PLANNER_LOC= os.path.join(DEFAULT_ROOT_DIR, "planners/descarwin/cpt-yahsp/release")
	PLANNER_EXEC_LOC= os.path.join(DEFAULT_ROOT_DIR, "planners/descarwin/cpt-yahsp/release/cpt_yahsp")
	PLANNER_PARAMS = ""

	return "(cd %s && %s && %s %s %s -o %s -f %s %s)"%(PLANNER_LOC,
		MEMLIMIT_CMD, TIME_CMD, TIMEOUT_CMD, PLANNER_EXEC_LOC,
		domainFile, probFile, PLANNER_PARAMS)
		
def fd_FF(domainFile, probFile, planFile=""):
	PLANNER_LOC= os.path.join(DEFAULT_ROOT_DIR, "planners/fd")
	PLANNER_EXEC_LOC= os.path.join(DEFAULT_ROOT_DIR, "planners/fd/fast-downward.py")
	PLANNER_PARAMS = "--heuristic \"hff=ff()\" --search \"lazy_greedy([hff], preferred=[hff])\""

	return "(cd %s && %s && %s %s %s %s %s %s)"%(PLANNER_LOC,
		MEMLIMIT_CMD, TIME_CMD, TIMEOUT_CMD, PLANNER_EXEC_LOC,
		domainFile, probFile, PLANNER_PARAMS)
		
def fd_blind(domainFile, probFile, planFile=""):
	PLANNER_LOC= os.path.join(DEFAULT_ROOT_DIR, "planners/fd")
	PLANNER_EXEC_LOC= os.path.join(DEFAULT_ROOT_DIR, "planners/fd/fast-downward.py")
	PLANNER_PARAMS = "--search \"astar(blind())\""

	return "(cd %s && %s && %s %s %s %s %s %s)"%(PLANNER_LOC,
		MEMLIMIT_CMD, TIME_CMD, TIMEOUT_CMD, PLANNER_EXEC_LOC,
		domainFile, probFile, PLANNER_PARAMS)
		
def madagascar(domainFile, probFile, planFile=""):
	PLANNER_LOC= os.path.join(DEFAULT_ROOT_DIR, "planners/MADAGASCAR/src")
	PLANNER_EXEC_LOC= os.path.join(DEFAULT_ROOT_DIR, "planners/MADAGASCAR/src/MpC")
	PLANNER_PARAMS = "-P 2"

	return "(cd %s && %s && %s %s %s %s %s %s)"%(PLANNER_LOC,
		MEMLIMIT_CMD, TIME_CMD, TIMEOUT_CMD, PLANNER_EXEC_LOC,
		domainFile, probFile, PLANNER_PARAMS)

def validate(domainFile, probFile, planFile):
	VALIDATOR_EXEC_CMD = os.path.join(DEFAULT_ROOT_DIR, VALIDATOR_EXEC)
	return "(%s %s %s %s %s)" % (VALIDATOR_EXEC_CMD,
		VALIDATOR_PARAMS, domainFile, probFile, planFile)

#Limit Commands
TIMEOUT_CMD="timeout -s SIGXCPU 30m" #30mins
TIME_CMD = "time -p"
MEMLIMIT_CMD="ulimit -Sv 4000000" #4GB

#Validation Parameters
VALIDATOR_EXEC = "VAL/validate"
VALIDATOR_PARAMS = "-t 0.001 -v"

#File Locations
LOG_FOLDER= "logs/"
PROBLEM_SETS= "problems/"
PLANS_FOLDER = "plans"
OUTPUT_FOLDER = "output"

#Constants
DOMAIN_FILE = "DOMAIN.PDDL"
IGNORE_SET_LIST = ["archive", "archive2", "archive3", "constraints_def"]
AIRPORT_PROBLEM = ["airport", "airport-tighten"]
NO_GOODS_PROBLEM = ["mmcr-no-metric-no-goods", "mmcr-no-metric-no-goods-10Cargo"]

PLANNERS_NEEDING_EXTRA_CONF = [	"tplanS1T0", 
								"tplanS1T1", 
								"tplanS2T0", 
								"tplanS2T1",
								"tplanS3T0", 
								"tplanS3T1",
								"tplanS4T0", 
								"tplanS4T1",
								"tplanS5T0", 
								"tplanS5T1"]
CONF_FILE_DIR = "constraints_def"
CONF_FILE_SUBDIR = {"tplanS1T0" : "1", 
					"tplanS1T1" : "1", 
					"tplanS2T0" : "2", 
					"tplanS2T1" : "2", 
					"tplanS3T0" : "2", 
					"tplanS3T1" : "2", 
					"tplanS4T0" : "3", 
					"tplanS4T1" : "3", 
					"tplanS5T0" : "3", 
					"tplanS5T1" : "3"}

CONF_FILE_NAMES = {	"satellite" : "satellite.conf",
					"satellite-tighten" : "satellite.conf",
					"pipesworld" : "pipesworld.conf",
					"pipesworld-tighten" : "pipesworld.conf",
					"mmcr-nometric" : "mmcr.conf",
					"crewplanning" : "crewplanning.conf"}

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
		"Colin-RPG" : colinRPG,
		#"NoSD-Colin-RPG" : colinRPGNoSD,
		"POPF-RPG" : popf,
		#"NoSD-POPF-RPG" : popfNoSD,
		#"Optic-RPG" : optic,
		#"Optic-SLFRP" : opticSLFRP,
		#"lpg-td" : lpgtd,
		"Colin-TRH-Colin" : colinTRHcolin,
		#"ablation-Colin-TRH-Colin": colinTRHcolinAblation,
		"Popf-TRH-Popf" : popfTRHpopf,
		#"ablation-Popf-TRH-Popf" : popfTRHpopfAblation,
		#"NoSD-Colin-TRH-Colin" : colinTRHcolinNoSD,
		#"NoSD-ablation-Colin-TRH-Colin": colinTRHcolinAblationNoSD,
		#"NoSD-Popf-TRH-Popf" : popfTRHpopfNoSD,
		#"NoSD-ablation-Popf-TRH-Popf" : popfTRHpopfAblationNoSD,
		#"MetricFF": metricff,
		#"fd_FF": fd_FF,
		#"fd_blind" : fd_blind,
		#"madagascar" : madagascar
		"tplanS0T0" : tplanS0T0, #All Ground Operators
		"tplanS0T1" : tplanS0T1,
		"tplanS1T0" : tplanS1T0, #Selective Ground Operators
		"tplanS1T1" : tplanS1T1,
		"tplanS2T0" : tplanS2T0, #Operator Add Effects
		"tplanS2T1" : tplanS2T1,
		"tplanS3T0" : tplanS3T0, #Most Recent Operator Add Effects
		"tplanS3T1" : tplanS3T1,
		"tplanS4T0" : tplanS4T0, #Operator Effects
		"tplanS4T1" : tplanS4T1,
		"tplanS5T0" : tplanS5T0, #Most Recent Operator Effects
		"tplanS5T1" : tplanS5T1,
		"tplanS6T0" : tplanS6T0, #End-Snap Action Ground Operator Effects
		"tplanS6T1" : tplanS6T1,
		"tplanS7T0" : tplanS7T0, #Start-Snap Action Ground Operator Effects
		"tplanS7T1" : tplanS7T1
	}
	#iterate through planners
	for planner in planners:
		#Get function to create planner command
		f = planners[planner]
		#iterate through problem sets
		problemDir = os.path.join(DEFAULT_ROOT_DIR, PROBLEM_SETS)
		
		for root, dirs, files in os.walk(problemDir):
			for subdir in dirs:
				if subdir in IGNORE_SET_LIST:
					continue
				#Get full problem path
				subdir_fullpath = os.path.join(root, subdir)
				#Ger full path for plan and logs
				plansdir_fullpath = os.path.join(DEFAULT_ROOT_DIR, LOG_FOLDER, planner, subdir, PLANS_FOLDER)
				outputdir_fullpath = os.path.join(DEFAULT_ROOT_DIR, LOG_FOLDER, planner, subdir, OUTPUT_FOLDER)
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
					elif subdir in NO_GOODS_PROBLEM:
						domainFile = os.path.join(subdir_fullpath,  prob[:-5] + "-" + DOMAIN_FILE)
						
					for itr in range(start, start+iterations):
						#Plan file
						planFileName = "%s-%i.plan"%(prob, itr)						
						planFile = os.path.join(plansdir_fullpath, planFileName)
						
						planner_command = ""
						if (planner in PLANNERS_NEEDING_EXTRA_CONF):
							if subdir not in CONF_FILE_NAMES:
								printMessage("Could not schedule %s - %s for %s as there\
 was no associated conf file."%(subdir, prob, planner))
								break #Can't schedule up this problem

							confFileName = CONF_FILE_NAMES[subdir]
							confFile = os.path.join(DEFAULT_ROOT_DIR, PROBLEM_SETS, 
								CONF_FILE_DIR, CONF_FILE_SUBDIR[planner], confFileName)
							planner_command = f(domainFile, probFile, planFile, confFile)
						else:
							#Planner command
							planner_command = f(domainFile, probFile, planFile)

						#Validate command
						validate_command = validate(domainFile, probFile, planFile)
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

"""
	CurrentAllocation is a dict that holds information about each worker.
	Information for each worker is stored in another dict that is indexed by ints, where:
	0 - is the IP address of the worker
	1 - is the hostname of the worker
	2 - is the name of the problem being solved or the status of the worker
	3 - is the iteration of that problem being solved
	4 - is the time that problem was started
	5 - is the number of problems solved by that worker
"""

def registerWorker(currentAllocation, _id, ip, hostname):
	if _id not in currentAllocation:
		currentAllocation[_id] = {}
		currentAllocation[_id][0] = ip
		currentAllocation[_id][1] = hostname
		currentAllocation[_id][5] = 0

	currentAllocation[_id][2] = WORKER_PAUSED
	currentAllocation[_id][3] = 0
	currentAllocation[_id][4] = time.time()
	
def updateWorkerState(currentAllocation, _id, state):
	currentAllocation[_id][2] = state
	currentAllocation[_id][3] = 0
	currentAllocation[_id][4] = time.time()
	
def updateWorkerJob(currentAllocation, _id, plannerName, problemName, itr):
	currentAllocation[_id][2] = "%s - %s"%(plannerName, problemName)
	currentAllocation[_id][3] = itr
	currentAllocation[_id][4] = time.time()
	currentAllocation[_id][5] += 1

def getCurrentAllocationString(currentAllocation, startTime, queueSize):
	result = ""
	workerTotalTime = time.time() - startTime
	for _id in currentAllocation:
		duration = time.time() - currentAllocation[_id][4]
		numberProcessed = currentAllocation[_id][5]
		seconds_per_problem = workerTotalTime / numberProcessed
		result += "%i: %s [%s]: %s-%i [Current Prob Time : %s] {Average Speed: %s / Prob}\n"%(_id,
			currentAllocation[_id][1], #Hostname
			currentAllocation[_id][0], #IP
			currentAllocation[_id][2], #Current State / planner-problem
			currentAllocation[_id][3], #Problem iteration
			str(datetime.timedelta(seconds=duration)), #Elapsed time for this problem
			str(datetime.timedelta(seconds=seconds_per_problem))) #Average problem speed

	result += "\nThere is %i problems remaining to be processed and %i currently processing.\n"%(queueSize, getNumberOfWorkersExecuting(currentAllocation))
	result += "\tThis is estimated to take %s to complete\n"%getEstimatedTimeRemaining(currentAllocation, startTime, queueSize)

	return result
	
def getEstimatedTimeRemaining(currentAllocation, startTime, queueSize):
	numberProcessed = 0
	for _id in currentAllocation:
		numberProcessed += currentAllocation[_id][5]
	
	if numberProcessed < 2 * len(currentAllocation):
		return "calculating..."
	
	time_remaining = ((time.time() - startTime) / numberProcessed) * queueSize
	
	return str(datetime.timedelta(seconds=time_remaining))

def getNumberOfWorkersExecuting(currentAllocation):
	numExecutions = 0
	for _id in currentAllocation:
		if currentAllocation[_id][2] not in [WORKER_PAUSED, WORKER_TERMINATED]:
			numExecutions += 1
	return numExecutions
	
def workersTerminated(currentAllocation):
	for _id in currentAllocation:
		if not currentAllocation[_id][2] is WORKER_TERMINATED:
			return False
	return True
	
def shutdownSocket(aSocket):
	aSocket.shutdown(socket.SHUT_RDWR)
	aSocket.close()
	time.sleep(1)

def main(args):

	_id = getInstanceID()
	printMessage("Started. My ID is %i"%_id)
	
	if len(args) > 1:
		if os.path.isdir(args[1]):
			global DEFAULT_ROOT_DIR
			DEFAULT_ROOT_DIR = args[1]
		else:
			printMessage("Error: Invalid direcory specified as experimentation directory: %s"%args[1])

	printMessage("Experimentation directory set to %s"%DEFAULT_ROOT_DIR) 

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
	startTime = time.time()

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
	restrictWorkers = False
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
			reply = getMessageString(_id, "Ack. Queue size is %i. Estimated time remaining is %s"%(q.qsize(), \
					getEstimatedTimeRemaining(currentAllocation, startTime, q.qsize())))
		elif message.message == REQUEST_PROBLEM:
			#Pause the worker because it is done.
			registerWorker(currentAllocation, message._id, addr[0], message.hostname)
			
			if q.empty(): #Tell the workers to terminate if done
				printMessage("Received request from machine %s with id %i, but queue is empty. Instructing worker to terminate."%(addr, 
							message._id))
				reply = getMessageString(_id, EXIT_PROCESS)
				
				updateWorkerState(currentAllocation, message._id, WORKER_TERMINATED)
			elif terminate:
				printMessage("Received request from machine %s with id %i, but have been instructed to terminate workers. Instructing worker to terminate."%(addr, 
							message._id))
				reply = getMessageString(_id, EXIT_PROCESS)
				updateWorkerState(currentAllocation, message._id, WORKER_TERMINATED)
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
				printMessage("Processing %s, %s for iteration %i on machine %s with id %i"%(job.plannerName, job.problemName, 
					job.itr, addr, message._id))
				reply = getMessageString(_id, job)
				updateWorkerJob(currentAllocation, message._id, job.plannerName, job.problemName, job.itr)
					
			if q.empty() and workersTerminated(currentAllocation):
				printMessage("Queue is empty and all workers have terminated. Shutting Down.")
				conn.sendall(reply)
				conn.shutdown(socket.SHUT_RDWR)
				conn.close()
				shutdownSocket(serversocket)
				break
		elif message.message == CURRENT_ALLOCATION:
			printMessage("Received request from machine %s with id %i for current allocation."%(addr, 
				message._id))
			reply = getMessageString(_id, 
				getCurrentAllocationString(currentAllocation, startTime, q.qsize()))
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
