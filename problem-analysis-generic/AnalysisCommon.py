#! /usr/bin/python
#Author: Tony Allard
#Date: 06 April 2016
#Description: Common methods for problem analysis

import re

TIMEOUT_DELIM = "timeout: the monitored command dumped core"
MEMORY_ERROR_DELIM = "terminate called after throwing an instance of \'std::bad_alloc\'"
EHC_SUCCESS = "EHC Success!!!!"
BFS_SUCCESS = "BFS Success!!!!"
COLIN_SUCCESS_DELIM = ";;;; Solution Found"
UNSOVLEABLE_DELIM = ";; Problem unsolvable!"
TERMINATE_FLAGS = [TIMEOUT_DELIM, MEMORY_ERROR_DELIM, EHC_SUCCESS, BFS_SUCCESS, COLIN_SUCCESS_DELIM, UNSOVLEABLE_DELIM, "Beginning the replay"]
SEARCH_SUCCESS_DELIM = "g"
SEARCH_FAILURE_DELIM = "Problem Unsolvable"
PDDL_FILE_EXT = ".pddl"
LOG_FILE_EXT = ".pddl.txt"
LOG_FILE_START_SEQ = "==="
LPGTD_SUCCESS_DELIM = " solution found: "
SEARCH_BEGIN_DELIM = "Initial heuristic = "
BRANCH_STRING_START = "[0-9]: "
NEW_HVAL_STRING = " \([0-9]+.[0-9]+ \| [0-9]+.[0-9]+\)"
RESORTING_TO_BFS = "Resorting to best-first search"

SERVER_LOG_DELIM = "explog-"

def filterBranchString(branch):
	branch = re.sub(NEW_HVAL_STRING, "", branch) #remove hvals
	branch = re.sub(BRANCH_STRING_START, "", branch) #remove starting delim
	branch = branch.partition(TIMEOUT_DELIM)[0] #remove timeouts
	branch = branch.partition(MEMORY_ERROR_DELIM)[0] #remove memory overruns
	branch = branch.partition(EHC_SUCCESS)[0] #remove success
	branch = branch.partition(BFS_SUCCESS)[0] #remove success
	branch = branch.partition(COLIN_SUCCESS_DELIM)[0] #remove success
	branch = branch.partition(UNSOVLEABLE_DELIM)[0] #remove success
	branch = branch.partition("Beginning the replay")[0] #remove success
	return branch

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
	if PDDL_FILE_EXT.lower() in filename[-len(PROBFILE_DELIM):].lower():
		return True
	return False

def isProblemLog(filename, file):
	if LOG_FILE_EXT in filename.lower() and LOG_FILE_START_SEQ in file[0][:3]:
		return True
	return False

def isServerLog(filename):
	if SERVER_LOG_DELIM in filename:
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