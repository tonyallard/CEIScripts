#! /usr/bin/python
#Author: Tony Allard
#Date: 06 April 2016
#Description: Common methods for problem analysis

TIMEOUT_DELIM = "timeout: the monitored command dumped core"
MEMORY_ERROR_DELIM = "terminate called after throwing an instance of \'std::bad_alloc\'"
PDDL_FILE_EXT = ".pddl"
LOG_FILE_EXT = ".pddl.txt"
SUCCESS_DELIM = ";;;; Solution Found"
UNSOVLEABLE_DELIM = ";; Problem unsolvable!"

SERVER_LOG_DELIM = "explog-"

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
		if SUCCESS_DELIM in line:
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

def isProblemLog(filename):
	if LOG_FILE_EXT in filename.lower():
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