#! /usr/bin/python
#Author: Tony Allard
#Date: 06 April 2016
#Description: Common methods for problem analysis

import os
import sys
import AnalysisCommon

SERVER_ATTEMPT_DELIM = "Processing "
LOG_FILE_EXT = ".txt"

def main(args):
	path = "/mnt/data/160406-Colin-RPG-logs/"
	server = ""

	serverProblems = []

	memFails = []
	timeoutFails = []
	NoFails = []

	#Find server log file
	for filename in os.listdir(path):
		if server in filename:
			serverLog = open(path+filename, 'r')

			#extract problems server attempted
			for line in serverLog:
				if SERVER_ATTEMPT_DELIM in line and server in line:
					problemName = line[line.index(SERVER_ATTEMPT_DELIM) + len(SERVER_ATTEMPT_DELIM):line.index(AnalysisCommon.PDDL_FILE_EXT)+len(AnalysisCommon.PDDL_FILE_EXT)]
					serverProblems.append(problemName)
			
	for problem in serverProblems:
		log = open(path+problem+LOG_FILE_EXT, 'r')
		seemsOK = True
		for line in log:
			#check problem for memory crash
			if AnalysisCommon.MEMORY_ERROR_DELIM in line:
				memFails.append(problem)
				seemsOk = False
			#check problem for timeout
			if AnalysisCommon.TIMEOUT_DELIM in line:
				timeoutFails.append(problem)
				seemsOK = False
		if seemsOK :
			NoFails.append(problem)

	#Print problems
	print "Problems that ran out of memory"
	for prob in memFails:
		print prob

	print "\nProblems that exceeded CPU time"
	for prob in timeoutFails:
		print prob

	print "\nProblems that seem OK"
	for prob in NoFails:
		print prob


#Run Main Function
if __name__ == "__main__":
	main(sys.argv)