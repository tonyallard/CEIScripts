#! /usr/bin/python3
#Author: Tony Allard
#Date: 06 April 2016
#Description: Common methods for problem analysis

import os
import re
import gzip

#Success Messages
EHC_SUCCESS = "EHC Success!!!!"
BFS_SUCCESS = "BFS Success!!!!"
COLIN_SUCCESS_DELIM = ";;;; Solution Found"
SEARCH_SUCCESS_DELIM = "g"
LPGTD_SUCCESS_DELIM = " solution found: "

#Timeout Error Messages
TIMEOUT_DELIM = "timeout: the monitored command dumped core"
LPG_TIMEOUT_DELIM = "Max time exceeded."

#Memory Error Messages
MEMORY_ERROR_DELIM = "terminate called after throwing an instance of \'std::bad_alloc\'"
MADAGASCAR_MEMORY_DELIM = "ERROR: Could not allocate more memory"
MADAGASCAR_OWN_ALLOC_MEMORY_DELIM = "MpC: clausesets.c:69: ownalloc: Assertion `ptr' failed."

#Segmentation Fault Messages
SEGMENTATION_FAULT = "Segmentation fault (core dumped)"
SEGMENTATION_FAULT_IN_SUB_CMD = "Command terminated by signal 11"

#Solution unable to be found
UNSOVLEABLE_DELIM = ";; Problem unsolvable!"
UNSOLVABLE_TPLAN = "Could not find solution."
SEARCH_FAILURE_DELIM = "Problem Unsolvable"

TERMINATE_FLAGS = [TIMEOUT_DELIM, MEMORY_ERROR_DELIM, EHC_SUCCESS, BFS_SUCCESS, COLIN_SUCCESS_DELIM, UNSOVLEABLE_DELIM, "Beginning the replay"]

#Log File Delimiters
LOG_FILE_START_SEQ = "==="
SEARCH_BEGIN_DELIM = "Initial heuristic = "
BRANCH_STRING_START = "[0-9]: "
NEW_HVAL_STRING = " \([0-9]+.[0-9]+ \| [0-9]+.[0-9]+\)"
RESORTING_TO_BFS = "Resorting to best-first search"
COMMAND_DELIM = "===with Command \((.*)\)==="
TIMEOUT_COMMAND = "timeout -s SIGXCPU [0-9]+m "
PLAN_VALIDATION = "Plan Validation"

#VAL Messages
VALIDATOR_PLAN_EXECUTE_SUCCESS = "Plan executed successfully - checking goal"
VALIDATOR_PLAN_EXECUTE_FAILURE = "Plan failed to execute"
VALIDATOR_PLAN_GOAL_FAILURE = "Goal not satisfied"
VALIDATOR_BAD_PLAN_DESCRIPTION = "Bad plan description!"
VALIDATOR_NO_PLAN = "Bad plan file!"
VALIDATOR_SUCCESS = "Successful plans:"
VALIDATOR_FAILURE = "Failed plans:"

#File Extentions
SERVER_LOG_DELIM = "explog-"
PDDL_FILE_EXT = ".pddl"
LOG_FILE_EXT = ".pddl.txt"
PLAN_FILE_EXT = ".plan"
COMPRESSED_LOG_FILE_EXT = ".txt.gz"
COMPRESSED_PLAN_FILE_EXT = ".plan.gz"
OUTPUT_DIR = "output"
PLANS_DIR = "plans"

#Other Constants
PLANNERS_THAT_WRITE_THEIR_OWN_PLAN_FILES = ["lpg-td"]

def filterBranchString(branch):
	branch = re.sub(NEW_HVAL_STRING, "", branch) #remove hvals
	branch = re.sub(BRANCH_STRING_START, "", branch) #remove starting delim
	branch = branch.partition(TIMEOUT_DELIM)[0] #remove timeouts
	branch = branch.partition(MEMORY_ERROR_DELIM)[0] #remove memory overruns
	branch = branch.partition(EHC_SUCCESS)[0] #remove success
	branch = branch.partition(BFS_SUCCESS)[0] #remove success
	branch = branch.partition(COLIN_SUCCESS_DELIM)[0] #remove success
	branch = branch.partition(UNSOVLEABLE_DELIM)[0] #remove success
	branch = branch.partition(RESORTING_TO_BFS)[0] #remove BFS Switch
	branch = branch.partition("Beginning the replay")[0] #remove success
	return branch
	
def getLogStructure(rootDir, logs=True):
	
	IGNORED_PROBLEMS = [ 
						"driverlogshift" #Driverlog shift is too different a format
						]

	logStructure = {}
	for planner in os.listdir(rootDir):
		plannerDir = os.path.join(rootDir, planner)
		
		if (not os.path.isdir(plannerDir)):
			continue
		
		logStructure[planner] = {}

		for problem in os.listdir(plannerDir):
			
			if problem in IGNORED_PROBLEMS:
				continue
			logDir = os.path.join(plannerDir, problem, OUTPUT_DIR)
			if (not logs):
				logDir = os.path.join(plannerDir, problem, PLANS_DIR)
			logStructure[planner][problem] = logDir
	return logStructure

def getPlanStructure(rootDir):
	return getLogStructure(rootDir, False)

def bufferCompressedFile(filename):
	with gzip.open(filename, 'rt') as f:
		try:
			buffer = bufferFile(f)
		except IOError:
			print("There was an error reading %s!"%filename)
			buffer = -1
		f.close()
		
	return buffer

def extractCommand(logFile):
	result = re.search(COMMAND_DELIM, logFile[1])
	return result.group(1)

def extractPlannerCommand(logFile):
	fullCmd = extractCommand(logFile)
	return re.split(TIMEOUT_COMMAND, fullCmd)[1]

def getDomain(logFile):
	plannerCmd = extractPlannerCommand(logFile)
	return re.split(" ", plannerCmd)[1]
	
def getProblem(logFile):
	plannerCmd = extractPlannerCommand(logFile)
	return re.split(" ", plannerCmd)[2]

def hasTimedOut(logFile):
	for line in logFile:
		if TIMEOUT_DELIM in line:
			return True
	return False

def isOutOfMemory(logFile):
	for line in logFile:
		if MEMORY_ERROR_DELIM in line:
			return True
	return False

def isCPUTimeout(logFile):
	for line in logFile:
		if TIMEOUT_DELIM in line:
			return True
	return False

def isSuccessful(logFile):
	for line in logFile:
		if COLIN_SUCCESS_DELIM in line:
			return True
	return False

def isUnsolveable(logFile):
	for line in logFile:
		if UNSOVLEABLE_DELIM in line:
			return True
	return False

def bufferFile(file):
	fileBuffer = []
	for line in file:
		fileBuffer.append(line)
	return fileBuffer

def isProblemFile(filename):
	if filename.lower().endswith(PDDL_FILE_EXT.lower()):
		return True
	return False
	
def isProblemLog(filename, file):
	if filename.lower().endswith(COMPRESSED_LOG_FILE_EXT.lower()) and \
		LOG_FILE_START_SEQ in file[0][:3]:
		return True
	return False

def isServerLog(filename):
	if filename.lower().endswith(SERVER_LOG_DELIM.lower()):
		return True
	return False

def checkArgs(arg, args):
	if args.count(arg) > 0:
		return True
	return False

def getTerminationIndex(line):
	index = line.find(TIMEOUT_DELIM)
	if index is -1:
		index = line.find(MEMORY_ERROR_DELIM)
	if index is -1:
		index = line.find(SEARCH_SUCCESS_DELIM)
	if index is -1:
		index = line.find(SEARCH_FAILURE_DELIM)
	return index
